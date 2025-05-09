# LAB04
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
## Lab instructions
#### Example 1: RAG based search using Llama-index and OpenAI synthesis
This code builds a vector index of documents using OpenAI embeddings, then queries it using either pure vector search (retrieval) or an LLM to generate natural-language answers.
It prints both the top-matching documents and, if enabled, a synthesized response from the LLM.  The vector store framework used in this code is `LlamaIndex`.
```
python3 ./RAG_01.py
```
#### Example 2: RAG based search using Chroma
```
python3 ./RAG_02.py
```
#### Example 3: RAG based search using Chroma and Langchain for synthesis (advanced)
```
python3 ./RAG_03.py
```
#### Example 4: RAG based search using OpenAI VectorStore and Response API
Create a managed VectorStore 
```
VS_ID=$(curl https://api.openai.com/v1/vector_stores \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "OpenAI-Beta: assistants=v2" \
  -d '{
    "name": "MCP documentation"
  }' | jq -r .id)
```
```
echo $VS_ID
```
File upload to OpenAI (purpose `assistants`)
```
FILE_ID=$(curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="assistants" \
  -F file="@data/llms-full.txt" | jq -r .id)
```
```
echo $FILE_ID
```
Link the file to the vector store (This can take a few seconds)
```
curl https://api.openai.com/v1/vector_stores/$VS_ID/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -H "OpenAI-Beta: assistants=v2" \
    -d '{
      "file_id": "'$FILE_ID'"    
  }'
```
<details>
<summary> Optionally add a pdf </summary>

```
curl -o ./data/attention.pdf https://arxiv.org/pdf/1706.03762
```
File upload
```
FILE_ID=$(curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="assistants" \
  -F file="@data/attention.pdf" | jq -r .id)
```
```
echo $FILE_ID
```
Link the file to the vector store (This can take a few seconds)
```
curl https://api.openai.com/v1/vector_stores/$VS_ID/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -H "OpenAI-Beta: assistants=v2" \
    -d '{
      "file_id": "'$FILE_ID'"    
  }'
```
</details>

Query the responses API
```
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4.1",
    "tools": [{
      "type": "file_search",
      "vector_store_ids": ["'$VS_ID'"]
    }],
    "input": "What are the differentiating features of MCP?"
  }' | jq -r '.output[].content[0].text'
```
Try another prompt, like "How can MCP influence attention in LLM reasoning?"

<details>
<summary> Sample Response </summary>
  
```
{
  "id": "resp_68150931fbf08191941ccd1dc614138202dc14dfaa548bfc",
  "object": "response",
  "created_at": 1746209074,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "id": "fs_68150932e7d48191a412727a3083ed2402dc14dfaa548bfc",
      "type": "file_search_call",
      "status": "completed",
      "queries": [
        "differentiating features of MCP",
        "What makes MCP unique",
        "MCP characteristics",
        "advantages of MCP",
        "MCP compared to other systems"
      ],
      "results": null
    },
    {
      "id": "msg_681509364dc88191873b04f106d66c6202dc14dfaa548bfc",
      "type": "message",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "annotations": [
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 437
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 899
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 899
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 1533
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 1533
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 2028
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 2028
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 2468
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 2468
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 2468
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 2750
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 2750
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 3245
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 3245
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 3245
            },
            {
              "type": "file_citation",
              "file_id": "file-9RiDWrjuYesyrYpXVJVCTP",
              "filename": "llms-full.txt",
              "index": 3245
            }
          ],
          "text": "Here are the key differentiating features of the Model Context Protocol (MCP):\n\n---\n\n## 1. **Standardization and Modularity**\n- **\u201cUSB-C for AI\u201d:** MCP serves as a universal adapter for AI applications, standardizing how they connect to various data sources and tools\u2014like USB-C did for hardware peripherals.\n- **Open Protocol:** Anyone can implement MCP to add integrations, benefiting from and contributing to a growing, open ecosystem.\n\n---\n\n## 2. **Separation of Concerns & Composability**\n- **Component Roles:**\n  - **Hosts** manage clients and coordinate AI/LLM integration.\n  - **Clients** maintain stateful, secure, one-to-one connections with servers.\n  - **Servers** expose resources, tools, and prompts, operating with focused responsibility.\n- **Composable Architecture:** Servers are isolated and composable; multiple servers can be combined without security risks or protocol conflicts.\n\n---\n\n## 3. **Capability Negotiation**\n- During initialization, clients and servers declare their supported features and negotiate the active feature set for their session, allowing optional and extensible functionality.\n\n---\n\n## 4. **Rich Feature Set**\n- **Resources:** Provides context and data to LLMs and users.\n- **Prompts:** Template workflows and message scaffolds.\n- **Tools:** Functions for the AI model to execute, exposing powerful capabilities.\n- **Sampling:** (Optional) Enables advanced agentic/recursive behaviors.\n- **Utilities:** Includes configuration, progress tracking, cancellation, error reporting, and logging.\n\n---\n\n## 5. **Security, Consent, and Isolation**\n- **Explicit User Consent:** All data and action access must be user-approved.\n- **Data Privacy:** User data is protected; servers only see the relevant context, not the full conversation or cross-server data.\n- **Tool Safety:** All tool executions require user authorization and clear explanations.\n- **Isolation:** Servers do not get access to each other's context\u2014enforced boundaries protect against data leaks, even among trusted components.\n\n---\n\n## 6. **Ease of Implementation & Extensibility**\n- **Servers are Easy to Build:** Servers focus on a narrow feature set; the host handles complex orchestration and coordination.\n- **Protocol Extensibility:** Features can be added incrementally to both servers and clients. Backwards compatibility is emphasized.\n- **Open Ecosystem:** Pre-built servers and clients, cross-platform SDKs, and integration with popular AI tools and IDEs.\n\n---\n\n## 7. **Ecosystem Integration**\n- **Wide Adoption:** Major tools (IDEs, chat apps, agentic frameworks) support MCP for seamless AI augmentation.\n- **Reusable Connectors:** Once a connector/server is built for a tool (e.g., Google Drive), any MCP-compatible client can use it.\n\n---\n\n## 8. **Focus on Powerful, Secure Agentic Workflows**\n- With MCP, LLMs can orchestrate actions\u2014like summarizing documents and scheduling meetings\u2014interacting securely and contextually with data and tools users already use.\n\n---\n\n**In summary**: MCP stands out due to its open, standardized, and modular approach that emphasizes security, composability, clear isolation, and protocol extensibility\u2014all designed to make building and scaling AI integrations faster, safer, and more powerful."
        }
      ],
      "role": "assistant"
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "service_tier": "default",
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [
    {
      "type": "file_search",
      "filters": null,
      "max_num_results": 20,
      "ranking_options": {
        "ranker": "auto",
        "score_threshold": 0.0
      },
      "vector_store_ids": [
        "vs_681506b3a9f881919ffe5373ed9e1cee"
      ]
    }
  ],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 18099,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 864,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 18963
  },
  "user": null,
  "metadata": {}
}
```
</details>

## Cleanup environment
```
./lab_cleanup.sh
```
