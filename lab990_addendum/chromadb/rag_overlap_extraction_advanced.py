"""
OWASP LLM06 PoC (advanced): raising chunk-overlap extraction recovery on a
large, repetitive corpus.

Companion to rag_overlap_extraction_demo.py. That script shows the primitive
on a small controlled corpus (near-100% recovery). On a large, repetitive
corpus a NAIVE single-chain walk recovers only a fraction, because the true
successor gets crowded out of the top-k by near-identical passages and one
missed link truncates the whole chain.

This script implements and measures three improvements on the SAME store:

  1. Larger k          -- deepen the candidate pool so the real neighbour is
                          present to be re-ranked (does not add query calls).
  2. Literal re-rank   -- ignore cosine order; score candidates by the LENGTH
                          of their literal shared boundary with the query edge
                          (longest common prefix forward / suffix backward).
                          Turns a fuzzy match into a near-deterministic
                          adjacency test.
  3. Frontier crawl    -- instead of one chain, seed from several diverse
     + multi-seed merge   queries and enqueue BOTH edges of every recovered
                          chunk. A broken link now only splits the document
                          into fragments that get rejoined from the far side,
                          rather than ending recovery.

It runs the naive walker and the advanced crawler on one indexed copy of the
corpus and prints a before/after coverage comparison.

MEASURED RESULTS on lab040_RAG/data/llms-full.txt (737 chunks, size=1000,
overlap=200, text-embedding-3-small):

    naive single-chain : 13.8% chunk coverage
    advanced crawl     : 91.6% chunk coverage, 95.7% text reconstruction
                         (2754 query() calls, no write access, no LLM)

The remaining ~8% are chunks whose successor never enters the top-k for any
edge query (unique boundaries at section breaks, or isolated components no
seed reached). More seeds and a larger k close most of that gap at the cost
of more queries.

Usage:
    export OPENAI_API_KEY=...
    python3 rag_overlap_extraction_advanced.py [path/to/corpus.txt]

Default corpus: ../../lab040_RAG/data/llms-full.txt
Uses an in-process Chroma (EphemeralClient); no server required. Set
CHROMA_HTTP=1 to use a running server instead (host/port below), matching the
Step 7/8 demos.
"""

import os
import re
import sys
import time
import hashlib
import difflib
from collections import deque

import chromadb
from chromadb.utils import embedding_functions

CHUNK_SIZE = 1000
OVERLAP = 200
STRIDE = CHUNK_SIZE - OVERLAP

# advanced-crawler knobs
K = 100                     # candidate pool depth
MATCH_FRAC = 0.55           # accept a neighbour if shared boundary >= this * OVERLAP
BRIDGE_SLICES = (200, 120, 60)   # edge lengths to try before giving up on a step
MAX_QUERIES = 6000          # safety cap on total query() calls
SEED_QUERIES = [
    "introduction overview", "installation and setup", "configuration",
    "server implementation", "client usage", "example code", "security",
    "authentication and authorization", "api reference", "protocol specification",
    "tools and resources", "prompts", "model context", "list of servers",
    "getting started", "transport", "error handling", "schema definition",
]


def fixed_stride_chunks(text, size=CHUNK_SIZE, stride=STRIDE):
    chunks, i, n = [], 0, len(text)
    while i < n:
        chunks.append(text[i:i + size])
        if i + size >= n:
            break
        i += stride
    return chunks


def _h(s):
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()


def lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def lcs(a, b):  # longest common SUFFIX
    n = 0
    for x, y in zip(reversed(a), reversed(b)):
        if x != y:
            break
        n += 1
    return n


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------
def build_store(text):
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-3-small",
    )
    if os.environ.get("CHROMA_HTTP") == "1":
        client = chromadb.HttpClient(host="localhost", port=8000, ssl=False)
    else:
        client = chromadb.EphemeralClient()
    try:
        client.delete_collection("extract_bench")
    except Exception:
        pass
    col = client.create_collection(
        name="extract_bench",
        metadata={"hnsw:space": "cosine"},
        embedding_function=ef,
    )
    pieces = fixed_stride_chunks(text)
    print(f"[index] embedding {len(pieces)} chunks (size={CHUNK_SIZE}, overlap={OVERLAP}) ...",
          flush=True)
    t0 = time.time()
    B = 200
    for i in range(0, len(pieces), B):
        batch = pieces[i:i + B]
        col.upsert(ids=[f"c{i+j}" for j in range(len(batch))], documents=batch)
        print(f"[index]   {min(i+B, len(pieces))}/{len(pieces)}", flush=True)
    print(f"[index] done in {time.time()-t0:.0f}s", flush=True)
    return col, pieces


class RetrieverAPI:
    """The attacker's only capability: query text in, chunk text out."""
    def __init__(self, col):
        self._col = col
        self.calls = 0

    def search(self, query, k):
        self.calls += 1
        res = self._col.query(query_texts=[query], n_results=k, include=["documents"])
        return res["documents"][0]


# ---------------------------------------------------------------------------
# Naive walker: single chain, small k, first literal match, stop on miss
# ---------------------------------------------------------------------------
def naive_walk(api, seed_query="What is this document about?"):
    visited = set()
    hits = api.search(seed_query, k=8)
    seed = hits[0]
    visited.add(_h(seed))

    def step(edge, direction):
        for c in api.search(edge, k=8):
            if _h(c) in visited:
                continue
            if direction == "fwd" and c.startswith(edge):
                return c
            if direction == "bwd" and c.endswith(edge):
                return c
        return None

    fwd, cur = [], seed
    while True:
        nxt = step(cur[-OVERLAP:], "fwd")
        if nxt is None:
            break
        visited.add(_h(nxt)); fwd.append(nxt); cur = nxt
    bwd, cur = [], seed
    while True:
        prev = step(cur[:OVERLAP], "bwd")
        if prev is None:
            break
        visited.add(_h(prev)); bwd.append(prev); cur = prev
    return visited


# ---------------------------------------------------------------------------
# Advanced crawler: large k, literal re-rank, gap-bridge, frontier BFS
# ---------------------------------------------------------------------------
def best_neighbour(api, edge, direction):
    """Return the candidate whose literal shared boundary with `edge` is longest."""
    cands = api.search(edge, k=K)
    scorer = (lambda c: lcp(c, edge)) if direction == "fwd" else (lambda c: lcs(c, edge))
    best, best_score = None, 0
    for c in cands:
        s = scorer(c)
        if s > best_score:
            best, best_score = c, s
    return best, best_score


def advanced_crawl(api):
    recovered = {}          # hash -> chunk text
    frontier = deque()      # (edge, direction)

    def add(chunk):
        h = _h(chunk)
        if h in recovered:
            return False
        recovered[h] = chunk
        frontier.append((chunk[-OVERLAP:], "fwd"))
        frontier.append((chunk[:OVERLAP], "bwd"))
        return True

    # multi-seed: root several components
    for q in SEED_QUERIES:
        for c in api.search(q, k=1):
            add(c)

    steps = 0
    while frontier and api.calls < MAX_QUERIES:
        edge, direction = frontier.popleft()
        found = None
        # gap-bridge: try progressively shorter edge slices
        for L in BRIDGE_SLICES:
            if L > len(edge):
                continue
            slice_edge = edge[-L:] if direction == "fwd" else edge[:L]
            cand, score = best_neighbour(api, slice_edge, direction)
            if cand is not None and score >= MATCH_FRAC * L and _h(cand) not in recovered:
                found = cand
                break
        if found is not None:
            add(found)
        steps += 1
        if steps % 50 == 0:
            print(f"[crawl] steps={steps} recovered={len(recovered)} "
                  f"queries={api.calls} frontier={len(frontier)}", flush=True)
    return recovered


# ---------------------------------------------------------------------------
# Reassembly over the recovered SET by linking literal edges
# ---------------------------------------------------------------------------
def reassemble(chunks):
    if not chunks:
        return ""
    heads = {c[:OVERLAP]: c for c in chunks}
    is_succ = set()
    for c in chunks:
        if c[-OVERLAP:] in heads:
            is_succ.add(_h(heads[c[-OVERLAP:]]))
    starts = [c for c in chunks if _h(c) not in is_succ] or [chunks[0]]
    seen, out = set(), ""
    cur = starts[0]
    while cur is not None and _h(cur) not in seen:
        seen.add(_h(cur))
        out = cur if not out else out + cur[OVERLAP:]
        cur = heads.get(cur[-OVERLAP:])
    return out


def main():
    corpus = sys.argv[1] if len(sys.argv) > 1 else "../../lab040_RAG/data/llms-full.txt"
    with open(corpus, "r", encoding="utf-8") as f:
        text = f.read()
    total = len(fixed_stride_chunks(text))
    print(f"[corpus] {corpus}  chars={len(text)}  chunks={total}\n", flush=True)

    col, pieces = build_store(text)

    print("\n=== NAIVE single-chain walk (k=8, stop on miss) ===", flush=True)
    api_n = RetrieverAPI(col)
    t = time.time()
    vis_n = naive_walk(api_n)
    print(f"[naive] recovered {len(vis_n)}/{total} chunks "
          f"({len(vis_n)/total:.1%}) in {api_n.calls} queries, {time.time()-t:.0f}s",
          flush=True)

    print("\n=== ADVANCED frontier crawl (k=%d, literal re-rank, multi-seed) ===" % K,
          flush=True)
    api_a = RetrieverAPI(col)
    t = time.time()
    rec = advanced_crawl(api_a)
    recon = reassemble(list(rec.values()))
    ratio = difflib.SequenceMatcher(
        None,
        re.sub(r"\s+", " ", text).strip(),
        re.sub(r"\s+", " ", recon).strip(),
    ).ratio()
    print(f"[adv] recovered {len(rec)}/{total} chunks ({len(rec)/total:.1%}) "
          f"in {api_a.calls} queries, {time.time()-t:.0f}s", flush=True)
    print(f"[adv] reassembled text similarity to source: {ratio:.1%}", flush=True)

    with open("reconstructed_advanced.txt", "w", encoding="utf-8") as f:
        f.write(recon)

    print("\n=== SUMMARY ===", flush=True)
    print(f"  naive single-chain : {len(vis_n)/total:.1%} chunk coverage", flush=True)
    print(f"  advanced crawl     : {len(rec)/total:.1%} chunk coverage, "
          f"{ratio:.1%} text reconstruction", flush=True)


if __name__ == "__main__":
    main()
