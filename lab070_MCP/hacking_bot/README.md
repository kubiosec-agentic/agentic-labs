## Getting started 

### Building a hacking container
```
docker build -t ubuntu-node-python .
```
### Starting the docker container
To get an interactive shell run
```
docker run -it ubuntu-node-python bash
```

## Starting it as remote powerfull MCP server
```
docker run -p 8000:8000 \
  -v ./traces:/tmp \
  -d ubuntu-node-python \
  npx -y supergateway --outputTransport streamableHttp \
  --stdio "npx -y @wonderwhy-er/desktop-commander@latest"
```

## Running a *hack*
```
python3 ./OA_pentester.py
```

## Configuring vscode for MCP
```
mkdir .vscode
```
```
cd .vscode 
```
Create `mcp.json`
```
{
	"servers": {
		"my-mcp-server-42b06837": {
			"url": "http://127.0.0.1:8000/mcp",
			"type": "http"
		}
	},
	"inputs": []
}
```
