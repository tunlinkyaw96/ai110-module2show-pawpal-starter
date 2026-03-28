# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Phase 4 added an algorithmic layer on top of the core scheduling engine:

| Feature | How it works |
|---|---|
| **Sort by time** | `Scheduler.sort_by_time()` orders any list of `ScheduledTask` objects by their `start_time` string. Zero-padded HH:MM strings compare correctly in lexicographic order, so no parsing overhead is needed. |
| **Filter by status / pet** | `Scheduler.filter_by_status()` narrows a flat task list to a single `TaskStatus` (e.g. COMPLETED vs PENDING). `Scheduler.filter_by_pet()` returns all tasks for a named pet from the owner's roster, enabling cross-pet queries. |
| **Recurring task auto-scheduling** | `Task.next_occurrence(from_date)` returns a fresh `Task` copy due the next day (DAILY) or next week (WEEKLY), with a reset status and new id. `Pet.mark_task_complete(task, today)` marks the task done and automatically appends the follow-up occurrence so the pet's task list always stays current. |
| **Conflict detection** | `Scheduler.detect_conflicts()` finds every `(a, b)` pair of `ScheduledTask` objects whose time windows overlap. `Scheduler.get_conflict_warnings()` wraps that result as human-readable warning strings so the caller can print or log them without crashing. |

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

| Test class | Behaviors verified |
|---|---|
| `TestTaskCompletion` | `mark_complete()`, `mark_skipped()`, and `reset()` each flip `TaskStatus` correctly |
| `TestTaskAddition` | `Pet.add_task()` appends tasks and they're retrievable; multiple adds work correctly |
| `TestSortingCorrectness` | `sort_tasks_by_priority()` returns tasks CRITICAL → HIGH → LOW; time-sensitive tasks outrank equal-priority non-sensitive tasks; `sort_by_time()` returns `ScheduledTask` objects in chronological order; both methods handle empty lists safely |
| `TestRecurrenceLogic` | DAILY tasks spawn a next-day follow-up; WEEKLY tasks spawn a next-week follow-up; ONCE tasks return `None`; `Pet.mark_task_complete()` auto-appends the follow-up; follow-ups get a fresh `id` and `PENDING` status |
| `TestConflictDetection` | Overlapping time windows are detected; back-to-back (non-overlapping) tasks are not flagged; `get_conflict_warnings()` returns human-readable strings; a single-task schedule never conflicts; the Scheduler's own slot assignment produces no internal conflicts |

### Confidence Level

**4 / 5 stars**

The core scheduling logic — priority sorting, recurrence, and conflict detection — is thoroughly covered by 22 automated tests, all of which pass. One star is withheld because the WEEKLY recurrence filter uses a hardcoded Mon/Wed/Fri heuristic rather than a stored start-date, and the Streamlit UI layer has no automated tests yet.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
