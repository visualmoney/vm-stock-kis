---
name: session-close
description: Writes the session-close dev log and re-queues next-up (max 3). Use when the user ends a session, asks for session close, or 세션 종료.
---

# Session close

Not a summary of the day's logs. Write what showed up **more than once**.

1. Write `docs/dev_logs/YYYY-MM-DD_nn_session_close.md` (`nn` = next sequence that day).
2. Re-label `next-up` — **at most 3** issues. Empty queue is a problem, not a rest state.
3. Open a `needs-decision` issue for any unresolved debate. Do not leave “decide later” only in the log.
4. Do not write a markdown To-Do list.
5. If a predecessor closed, remove `blocked` from dependents.
6. `git fetch --prune`. Delete local topic branches whose name is a merged PR
   head, or whose upstream is `[gone]`. Use `git branch -D` after squash.
   Never delete `main`.

Do not commit unless the user asked. Do not invent issue counts in the log; `gh issue list` if a number is needed.
