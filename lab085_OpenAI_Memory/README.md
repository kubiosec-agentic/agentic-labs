![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB085: OpenAI Agents with Memory Persistence

## Introduction

The OpenAI Agents SDK manages conversation memory through **sessions**.
A session stores conversation history and automatically feeds it back
into the agent on the next turn, so you never have to manually track
`previous_response_id` or call `.to_input_list()`.

This lab covers the four patterns you will use most often:

| Example | File | What it covers |
|---------|------|---------------|
| 1 | `OA_01.py` | Basic multi-turn memory with SQLiteSession |
| 2 | `OA_02.py` | Multiple sessions (separate users, same database) |
| 3 | `OA_03.py` | Compaction for long conversations |
| 4 | `OA_04.py` | Session operations: retrieve, limit, pop, clear |

## Set up your environment

```bash
export OPENAI_API_KEY="sk-..."
```

```bash
./lab_setup.sh
source .lab085/bin/activate
```

## Exercises

### 1. Basic memory

The simplest case: one agent, one session, three turns. The agent
remembers previous answers without any manual state management.

```bash
python3 OA_01.py
```

Ask "What city is the Golden Gate Bridge in?", then "What state is it
in?", then "What's the population?". The agent resolves "it" correctly
because the session holds the full conversation history.

### 2. Multiple sessions

Two users, same database, separate histories. Each `SQLiteSession` is
identified by a session ID; different IDs never see each other's
messages.

```bash
python3 OA_02.py
```

This is the pattern for multi-tenant applications: one SQLite file (or
one Redis/Postgres instance), many session IDs.

### 3. Compaction

As conversations grow, raw history wastes tokens and can exceed the
context window. `OpenAIResponsesCompactionSession` wraps any session
and automatically summarizes older turns once a threshold is reached.

```bash
python3 OA_03.py
```

After six turns the session triggers compaction. The final
`get_items()` call shows fewer items than you would expect, because
the older turns have been replaced by a summary.

### 4. Session operations

Direct access to session contents: retrieve all items, limit how many
are fed to the agent, pop the last item, and clear the session
entirely.

```bash
python3 OA_04.py
```

`SessionSettings(limit=N)` is useful when you want to keep the full
history on disk but only feed the last N items as context for a given
run.

## Session types at a glance

The SDK ships several session backends. This lab uses SQLiteSession
because it needs no infrastructure, but the API is identical across
all backends:

| Session type | Backend | When to use |
|-------------|---------|-------------|
| `SQLiteSession` | Local SQLite file | Development, single-process apps |
| `AsyncSQLiteSession` | aiosqlite | Same, when you need non-blocking I/O |
| `RedisSession` | Redis | Distributed systems, shared memory across workers |
| `SQLAlchemySession` | Any SQLAlchemy DB | Production with Postgres, MySQL, etc. |
| `DaprSession` | Dapr state store | Cloud-native with 30+ backend options |
| `AdvancedSQLiteSession` | SQLite | Branching, usage analytics, turn-level queries |
| `EncryptedSession` | Wraps any session | Encryption at rest for sensitive conversations |
| `OpenAIConversationsSession` | OpenAI API | Server-managed storage at OpenAI |

Switching backends is a one-line change: replace the session
constructor and everything else stays the same.

## Key concepts

- **Session**: stores and retrieves conversation history for a given ID.
- **Runner.run(..., session=)**: the SDK calls `session.get_items()`
  before the run and `session.add_items()` after.
- **Compaction**: summarizes old turns to keep the session small.
- **SessionSettings(limit=N)**: caps how many items are retrieved,
  without deleting anything from the session.
- **Branching** (AdvancedSQLiteSession): create alternative
  conversation paths from any turn, useful for A/B testing agent
  behavior.

## Cleanup

```bash
deactivate
```

```bash
./lab_cleanup.sh
rm -f conversations.db   # if created by OA_02
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
