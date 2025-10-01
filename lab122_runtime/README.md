## Prerequisites
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


## Filters
### Egress Tracing Filter
```
jq -r '
  select(.process_kprobe != null)
  | {
      process_binary: .process_kprobe.process.binary,
      parent_binary: .process_kprobe.parent.binary,
      root_binary: (if .process_kprobe.parent.parent_binary? then .process_kprobe.parent.parent_binary
                   else .process_kprobe.parent.binary
                   end),
      resolved_binary: (if .process_kprobe.process.binary == "/proc/self/exe"
                        then .process_kprobe.parent.binary
                        else .process_kprobe.process.binary
                        end),
      saddr: .process_kprobe.args[0].sock_arg.saddr,
      sport: .process_kprobe.args[0].sock_arg.sport,
      daddr: .process_kprobe.args[0].sock_arg.daddr,
      dport: .process_kprobe.args[0].sock_arg.dport
    }
'
```
```
jq -r '
  select(.process_kprobe != null)
  | {
      process_binary: .process_kprobe.process.binary,
      process_args: .process_kprobe.process.arguments,
      parent_binary: .process_kprobe.parent.binary,
      parent_args: .process_kprobe.parent.arguments,
      root_binary: (if .process_kprobe.parent.parent_binary? then .process_kprobe.parent.parent_binary
                   else .process_kprobe.parent.binary
                   end),
      resolved_binary: (if .process_kprobe.process.binary == "/proc/self/exe"
                        then .process_kprobe.parent.binary
                        else .process_kprobe.process.binary
                        end),
      saddr: .process_kprobe.args[0].sock_arg.saddr,
      sport: .process_kprobe.args[0].sock_arg.sport,
      daddr: .process_kprobe.args[0].sock_arg.daddr,
      dport: .process_kprobe.args[0].sock_arg.dport
    }
'
```
