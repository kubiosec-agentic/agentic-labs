# LAB110 A2A
## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab110/bin/activate
```
## Lab instructions
### Setup Hello World Agent
```
git clone https://github.com/a2aproject/a2a-samples.git
cd a2a-samples/samples/python/agents/helloworld
uv run .
```
### Setup Hello World Client

```
cd a2a-samples/samples/python/agents/helloworld
```
```
uv run test_client.py
```
```
curl http://127.0.0.1:9999/.well-known/agent-card.json | jq -r .
```


### Setup A2A Inspector
```
git clone https://github.com/a2aproject/a2a-inspector.git
cd a2a-inspector/
uv sync
cd frontend
npm install
cd ..
chmod +x scripts/run.sh
bash scripts/run.sh
```

## Cleanup environment
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
