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
### MagenticOne
```
pip install "autogen-agentchat" "autogen-ext[magentic-one,openai]"
```
```
# If using the MultimodalWebSurfer, you also need to install playwright dependencies:
playwright install --with-deps chromium
```
```
python3 AG_03.py
```
## Cleanup environment
```
./lab_cleanup.sh
```
