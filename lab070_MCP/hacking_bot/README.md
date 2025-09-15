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
docker run -p 8000:8000 -d ubuntu-node-python npx -y supergateway --outputTransport streamableHttp  --stdio "npx -y @wonderwhy-er/desktop-commander@latest"
```
