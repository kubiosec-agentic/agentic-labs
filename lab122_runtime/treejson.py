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
            # exits don't add children, but they help populate proc info
    return procs, children


def print_tree(exec_id, procs, children, prefix="", is_last=True):
    p = procs.get(exec_id, {})
    if not p:
        return
    connector = "└── " if is_last else "├── "
    desc = f"{p.get('binary', '?')} (pid {p.get('pid', '?')})"
    args = p.get("arguments", "")
    if args:
        desc += f" {args}"
    print(prefix + connector + desc)

    child_ids = children.get(exec_id, [])
    for i, child in enumerate(child_ids):
        extension = "    " if is_last else "│   "
        print_tree(child, procs, children, prefix + extension, i == len(child_ids) - 1)


if __name__ == "__main__":
    # read JSON lines from stdin or file
    lines = sys.stdin.read().strip().splitlines()
    events = load_events(lines)
    procs, children = build_tree(events)

    # find root(s): those without parents
    all_children = {c for cl in children.values() for c in cl}
    roots = [eid for eid in procs if eid not in all_children]

    for i, r in enumerate(roots):
        p = procs.get(r, {})
        desc = f"{p.get('binary', '?')} (pid {p.get('pid', '?')})"
        args = p.get("arguments", "")
        if args:
            desc += f" {args}"
        print(desc)
        child_ids = children.get(r, [])
        for j, child in enumerate(child_ids):
            print_tree(child, procs, children, "", j == len(child_ids) - 1)
