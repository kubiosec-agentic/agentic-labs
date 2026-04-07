# Chroma v2 RAG Risks and the OWASP LLM Top-10

When you add a vector database to an LLM pipeline, you add a new attack surface. This document maps each OWASP LLM Top-10 risk to concrete ways it can show up with a Chroma v2 server, and lists quick mitigations you can apply today.

Use this alongside the hands-on walkthrough in the [README](./README.md) and the RAG lab in [lab040_RAG](../../lab040_RAG/).

| # | OWASP Risk | How it shows up with Chroma v2 | Quick mitigations |
|---|-----------|-------------------------------|-------------------|
| LLM01 | Prompt Injection | Retrieved chunks can contain hidden instructions that steer the model. Similarity search optimizes for semantic proximity, not safety. | Retrieval-time content filtering, instruction firewalls, strict output schemas, "reader" prompts that treat retrieved text as untrusted data. |
| LLM02 | Insecure Output Handling | Your app may act on model output derived from Chroma without sanitizing it, leading to command/SQL/HTTP calls based on attacker-planted text. | Treat model output as data. Escape, validate, and sandbox. Never pipe model text to shells or drivers without validation. |
| LLM03 | Training Data Poisoning | Poisoned docs upserted to Chroma skew retrieval or teach the system wrong patterns. Even "read-only" inference gets poisoned at the retrieval layer. | Write-path controls. Moderation on upsert. Provenance and signer metadata on docs. Periodic audits for indicators of poisoning. |
| LLM04 | Model Denial of Service | Large vectors, massive upsert batches, unbounded `n_results`, or many concurrent query calls can starve the app or the embedder. | Rate limits per tenant and API key. Cap payload sizes and `n_results`. Add timeouts and circuit breakers. Back-pressure on ingestion workers. |
| LLM05 | Supply Chain Vulnerabilities | Chroma Docker image, client SDKs, and embedding libs are dependencies. A compromised image or lib exposes the data path. | Pin versions and SBOMs, scan images, verify signatures, restrict egress from the DB host. |
| LLM06 | Sensitive Information Disclosure | Embeddings and stored documents may contain secrets or personal data. Cross-tenant or cross-database exposure is catastrophic. | Use Chroma v2 tenants and databases for isolation, enforce auth at the gateway, encrypt in transit, consider encrypting at rest, avoid returning raw embeddings to untrusted callers. |
| LLM07 | Insecure Plugin Design | In an agentic app, the "vector store" is effectively a tool. If the model has write or delete access via the HTTP client, you hand it mutation power. | Split read vs write identities. Give the model a read-only client. Human-in-the-loop or policy checks for mutations. Tool schemas that disallow destructive ops by default. |
| LLM08 | Excessive Agency | The model can autonomously create collections, exfiltrate hits, or chain queries to enumerate your corpus. | Capability minimization: only expose query on a scoped collection. No list-collections. No admin routes. Require approvals for broadened scopes. |
| LLM09 | Overreliance | Treating nearest neighbors as ground truth leads to confident but wrong answers when the neighborhood is weak. | Calibrate with similarity thresholds, cross-encoders or re-rankers, retrieval provenance in the answer, abstention paths when confidence is low. |
| LLM10 | Model Theft | Systematic scraping of embeddings or documents lets attackers reconstruct proprietary data or shadow your knowledge base. | Throttle queries, watermark content outside the DB, per-tenant keys, anomaly detection on query patterns, never return embeddings to untrusted users. |

## Chroma v2 specifics worth leaning on

Tenants and databases are first-class in v2. Use them to segment customers, teams, and environments, then place network and identity boundaries on top.

Expose the server only behind a gateway with TLS and auth. Treat the `/collections/*/upsert`, `/query`, and any list endpoints as sensitive surfaces.

## Minimal hardening checklist

**Network:** Bind Chroma to localhost, expose via a reverse proxy with TLS, WAF rules, and per-route auth.

**AuthZ:** Read-only token for the model's retrieval tool, separate write token for ingestion workers.

**Abuse limits:** Cap `n_results`, payload size, and QPS per tenant. Set timeouts.

**Poisoning guardrails:** Validate and scan docs on ingestion, attach source provenance in `metadatas`, and audit collections.

**Privacy:** Avoid returning `include=["embeddings"]` to frontends. Keep PII out of embeddings when possible.

**Observability:** Log retrieval prompts, top-k hits, and decisions. Alert on spikes in miss rates or unusual query vectors.

**Supply chain:** Pin and scan the Chroma image and clients. Track with SBOMs.

## See it in action

The [rag_poisoning_demo.py](./rag_poisoning_demo.py) script demonstrates LLM01 and LLM03 in a live Chroma environment: it upserts a poisoned document, shows how it hijacks the LLM's answer, and then applies an instruction firewall as mitigation. Run it after completing the [walkthrough](./README.md).
