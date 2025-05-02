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
File upload
```
FILE_ID =$(curl https://api.openai.com/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F purpose="fine-tune" \
  -F file="@data/llms-full.txt")
```
Link the file to the vector store
```
curl https://api.openai.com/v1/vector_stores/$VS_ID/files \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    -H "OpenAI-Beta: assistants=v2" \
    -d '{
      "file_id": "'$FILE_ID'"    
  }'
```
```
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4.1",
    "tools": [{
      "type": "file_search",
      "vector_store_ids": ["$VS_ID"],
      "max_num_results": 20
    }],
    "input": "What are the differentiating features of MCP?"
  }'
```
## Cleanup environment
```
./lab_cleanup.sh
```
