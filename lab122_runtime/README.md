## Pre-quisites
Install tetragon https://tetragon.io/docs/getting-started/install-docker/

## Test
```
docker exec -ti tetragon tetra getevents -o compact
```
```
docker exec -ti tetragon tetra getevents >events.jsonl
```
```
python treejson.py < events.jsonl
```
