---
name: port-triage
description: Triage a raw nmap/masscan style port listing into a prioritised findings table with a recommended next action per service. Use when the user pastes or points to a port scan.
---

# Port triage

## When to use
The user supplies scan output (nmap, masscan, netstat) or a file containing one.

## Procedure
1. Parse every `PORT STATE SERVICE` line. Ignore closed/filtered ports.
2. Classify each open port with this table:

| Port(s)            | Severity | Why                                            | Next action                                  |
|--------------------|----------|------------------------------------------------|----------------------------------------------|
| 21, 23, 512-514    | high     | cleartext auth protocols                       | disable, replace with SSH                    |
| 445, 139           | high     | SMB exposed                                    | firewall to management VLAN only             |
| 3389, 5900         | high     | remote desktop exposed                         | put behind VPN / bastion                     |
| 2375, 2376         | critical | Docker API                                     | bind to localhost, enable TLS client auth    |
| 6443, 10250        | critical | Kubernetes API / kubelet                       | verify authn/authz, restrict source ranges   |
| 22                 | medium   | SSH                                            | key-only auth, fail2ban, restrict sources    |
| 80                 | medium   | plain HTTP                                     | redirect to 443, HSTS                        |
| 443                | low      | HTTPS                                          | check cert, TLS config                       |
| 3306, 5432, 6379   | high     | database / cache directly reachable            | firewall, require auth, no public bind       |
| anything else      | info     | unknown                                        | identify the service, then re-triage         |

3. Write the result to `/triage/<host>.md` as a markdown table sorted by
   severity (critical first), followed by a "Top 3 actions" list.
4. Report the count per severity in your final answer, nothing else.

## Style
Do not speculate about CVEs. Base severity only on the table above.
