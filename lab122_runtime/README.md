![Security](https://img.shields.io/badge/Security-red) ![Docker](https://img.shields.io/badge/Docker-blue) ![Python](https://img.shields.io/badge/Python-blue)

# LAB122: Runtime Security Monitoring

## Introduction

This lab demonstrates runtime security monitoring using Tetragon, a runtime security tool that provides real-time visibility into container and system behavior for agentic AI applications. You'll learn how to capture, analyze, and visualize security events.

## Set up your environment

### Prerequisites

Install Tetragon: https://tetragon.io/docs/getting-started/install-docker/

### Setup Commands

```bash
export OPENAI_API_KEY="xxxxxxxxx"
```

```bash
./lab_setup.sh
```

```bash
source .lab122/bin/activate
```

## Lab instructions

### Test

```bash
docker exec -ti tetragon tetra getevents -o compact
```

```bash
docker exec -ti tetragon tetra getevents >events.jsonl
```

```bash
python treejson.py < events.jsonl
```

### Egress Tracing Filter

```bash
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

```bash
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

## Cleanup environment

```bash
deactivate
```

```bash
./lab_cleanup.sh
```
Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)