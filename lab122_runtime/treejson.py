^Cubuntu@ip-172-31-2-51:~cat treejson.py
import json
import sys
from collections import defaultdict

def load_events(lines):
    """Parse lines of JSON into process events."""
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events

def build_tree(events):
    """Build process tree mapping from exec/exit events."""
    procs = {}
    children = defaultdict(list)

    for ev in events:
        if "process_exec" in ev:
            p = ev["process_exec"]["process"]
            parent = ev["process_exec"]["parent"]
            procs[p["exec_id"]] = p
            procs[parent["exec_id"]] = parent
            children[parent["exec_id"]].append(p["exec_id"])
        elif "process_exit" in ev:
            p = ev["process_exit"]["process"]
            procs[p["exec_id"]] = p
            # exits don’t add children, but they help populate proc info
    return procs, children

def print_tree(exec_id, procs, children, indent=""):
    p = procs.get(exec_id, {})
    if not p:
        return
    desc = f"{p.get('binary', '?')} (pid {p.get('pid','?')})"
    args = p.get("arguments", "")
    if args:
        desc += f" {args}"
    print(indent + desc)
    for child in children.get(exec_id, []):
        print_tree(child, procs, children, indent + "   └─ ")

if __name__ == "__main__":
    # read JSON lines from stdin or file
    lines = sys.stdin.read().strip().splitlines()
    events = load_events(lines)
    procs, children = build_tree(events)

    # find root(s): those without parents
    all_children = {c for cl in children.values() for c in cl}
    roots = [eid for eid in procs if eid not in all_children]

    for r in roots:
        print_tree(r, procs, children)
ubuntu@ip-172-31-2-51:~$
