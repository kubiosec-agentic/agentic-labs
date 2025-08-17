# LAB930
## Set up your environment
```
export OPENAI_API_KEY="xxxxxxxxx"
```
```
./lab_setup.sh
```
```
source .lab930/bin/activate
```
## Lab instructions
### MemO SAAS
```
export MEM0_API_KEY="xxxxxxx"

```
### Qdrant Storage for Mem0
```
docker run -d --name qdrant \
   -p 6333:6333 -p 6334:6334 \
   -v $PWD/qdrant_storage:/qdrant/storage \
   qdrant/qdrant:latest
```


## Cleanup environment
```
docker stop qdrant
```
```
deactivate
```
```
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
