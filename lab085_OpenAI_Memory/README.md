![OpenAI](https://img.shields.io/badge/OpenAI-lightblue) ![Python](https://img.shields.io/badge/Python-blue) ![Agents](https://img.shields.io/badge/Agents-orange)

# LAB085: OpenAI Agents with Memory Persistence

## Introduction

When you build a chatbot or agent, every new API call starts with a
blank slate. The model has no idea what you said ten seconds ago unless
you explicitly pass the conversation history. Managing that history
yourself (appending messages, trimming context, handling token limits)
is tedious and error-prone.

The OpenAI Agents SDK solves this with **sessions**. A session is a
persistent store that holds conversation history and automatically
feeds it back into the agent on every turn. You create a session once,
pass it to `Runner.run()`, and the SDK handles the rest: it calls
`session.get_items()` before the run to load context, and
`session.add_items()` after the run to save the new messages.

This lab walks through four progressively more advanced patterns:

| Exercise | File | What it covers |
|----------|------|----------------|
| 1 | `OA_01.py` | Basic multi-turn memory with SQLiteSession |
| 2 | `OA_02.py` | Interactive chat with named sessions (persistence across runs) |
| 3 | `OA_03.py` | Compaction: automatic summarization of long conversations |
| 4 | `OA_04.py` | Session operations: retrieve, limit, pop, clear |

## Why does this matter?

In production agentic systems, memory management is a critical
concern:

- **Token cost**: sending the full history on every call wastes money.
  Compaction (exercise 3) solves this by summarizing older turns.
- **Multi-tenancy**: multiple users share the same infrastructure but
  must never see each other's conversations. Session IDs (exercise 2)
  enforce isolation.
- **Debugging**: when an agent misbehaves, you need to inspect what it
  actually "saw". Session operations (exercise 4) let you retrieve,
  trim, and replay history.
- **Security**: sensitive conversations need encryption at rest.
  `EncryptedSession` wraps any session backend with AES encryption.

## Set up your environment

```bash
export OPENAI_API_KEY="sk-..."
```

```bash
./lab_setup.sh
source .lab085/bin/activate
```

## Exercises

### 1. Basic multi-turn memory

The simplest case: one agent, one session, three scripted turns. The
agent remembers previous answers without any manual state management.

```bash
python3 OA_01.py
```

The script asks "What city is the Golden Gate Bridge in?", then "What
state is it in?", then "What's the population?". The agent resolves
"it" correctly each time because the session holds the full
conversation history.

Look at the code: there is no message list, no `previous_response_id`,
no `.to_input_list()`. The session does all of that behind the scenes.

### 2. Interactive chat with named sessions

This is the exercise you will use most in practice. The agent asks for
your name and uses it as the session ID. Type messages, get responses,
and quit with `exit`.

```bash
python3 OA_02.py
```

The key insight: **run it twice with the same name**. The second time,
the agent picks up exactly where you left off because the session is
persisted in `conversations.db`. Use a different name and you get a
fresh conversation, but the old one is still there.

This is the pattern for multi-tenant applications: one SQLite file (or
one Redis/Postgres instance), many session IDs. Each ID is fully
isolated.

Try this sequence:

1. Run with name "alice", tell the agent your favorite color.
2. Quit, then run again with name "alice", ask "What's my favorite color?"
3. Run with name "bob", ask the same question. Bob gets no answer.

### 3. Compaction for long conversations

As conversations grow, raw history wastes tokens and can exceed the
context window. `OpenAIResponsesCompactionSession` wraps any session
and automatically summarizes older turns once a threshold is reached.
The summary replaces the raw history, keeping the session small while
preserving the important context.

```bash
python3 OA_03.py
```

The script asks six questions about France and the Eiffel Tower, then
prints how many items remain in the session. You will see fewer items
than the twelve you would expect (six questions + six answers), because
older turns have been compacted into a summary.

This is essential for long-running agents, customer support bots, or
any scenario where conversations can run to hundreds of turns.

### 4. Session operations

Direct access to session contents: retrieve all items, limit how many
are fed to the agent, pop the last item, and clear the session
entirely. This is your debugging and memory management toolkit.

```bash
python3 OA_04.py
```

Key APIs demonstrated:

- `session.get_items()`: retrieve the full history
- `SessionSettings(limit=N)`: cap how many items the agent sees
  (without deleting anything from the session)
- `session.pop_item()`: remove the last item (useful for "undo")
- `session.clear_session()`: wipe everything (useful for "forget me")

## Session types at a glance

The SDK ships several session backends. This lab uses `SQLiteSession`
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

## How sessions work under the hood

```
Runner.run(agent, "Hello", session=session)
    |
    +--> session.get_items()          # load history
    |        |
    |        v
    +--> OpenAI Responses API call    # history + new message
    |        |
    |        v
    +--> session.add_items(response)  # save new turn
    |
    v
  result.final_output
```

The session is just a key-value store keyed by session ID. The SDK
never sends the session ID to OpenAI; it only sends the conversation
items. This means your session backend can be anything that implements
`get_items()`, `add_items()`, `pop_item()`, and `clear_session()`.

## Key concepts

- **Session**: stores and retrieves conversation history for a given ID.
- **Runner.run(..., session=)**: the SDK calls `session.get_items()`
  before the run and `session.add_items()` after.
- **Compaction**: summarizes old turns to keep the session small.
  Triggered automatically when the token count crosses a threshold.
- **SessionSettings(limit=N)**: caps how many items are retrieved,
  without deleting anything from the session. Good for cost control.
- **Branching** (AdvancedSQLiteSession): create alternative
  conversation paths from any turn, useful for A/B testing agent
  behavior.
- **Encryption** (EncryptedSession): wraps any session with AES
  encryption. Conversations are encrypted before they hit the database
  and decrypted on read. Required for sensitive data.

## Cleanup

```bash
deactivate
```

```bash
./lab_cleanup.sh
rm -f conversations.db   # if created by OA_02
```

Back to [Lab Overview](https://github.com/kubiosec-agentic/agentic-labs/blob/master/README.md#-lab-overview)
