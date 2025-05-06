# LAB08
## Set up your environment
```
export OPENAPI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
## Lab instructions
### Agent using MCP
```
python3 AG_01.py
```
### Agent Group Chat
```
python3 AG_02.py
```
### MultimodalWebSurfer (Only works on a MAC)
```
python3 AG_03.py
```
### MagenticOne
```
pip install "autogen-agentchat" "autogen-ext[magentic-one,openai]"
```
```
# If using the MultimodalWebSurfer, you also need to install playwright dependencies:
playwright install --with-deps chromium
```
```
python3 AG_04.py
```
### Cool extra
- https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/components/command-line-code-executors.html#docker
- https://arxiv.org/abs/2411.04468
- https://microsoft.github.io/autogen/stable//user-guide/core-user-guide/framework/distributed-agent-runtime.html#

## Cleanup environment
```
./lab_cleanup.sh
```
