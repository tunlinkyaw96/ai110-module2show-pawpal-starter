# PawPal+ — Smart Pet Care Planner

**PawPal+** is a Streamlit app that helps a busy pet owner build a daily care schedule for their pets. It combines a clean UI with a real scheduling engine: tasks are ranked by priority, slotted into a time budget, and any conflicts or overruns are surfaced as clear warnings.

---

## Features

| Feature | How it works |
|---|---|
| **Owner & pet profiles** | Create an owner with a daily time budget (minutes/day) and add multiple pets. All state persists in the browser session. |
| **Task builder** | Add tasks with title, category (walk, feeding, medication, grooming, enrichment, appointment, vet checkup), priority (LOW → CRITICAL), duration, recurrence, preferred time of day, and a time-sensitivity flag. |
| **Priority-based sorting** | `Scheduler.sort_tasks_by_priority()` ranks tasks by `priority_score()` — CRITICAL first, then HIGH, MEDIUM, LOW. Time-sensitive tasks get a +1 bonus so they beat same-priority peers. |
| **Daily schedule generation** | `Scheduler.generate_daily_plan()` filters tasks by recurrence, sorts by priority, and slots them sequentially from your chosen start time. Tasks that exceed the daily budget are skipped with an explanation. |
| **Chronological display** | `Scheduler.sort_by_time()` re-orders the generated plan earliest-to-latest so the owner reads it like a real calendar. |
| **Budget overrun warning** | Before generating, the app checks if total task time exceeds the daily budget and warns which tasks will be dropped. |
| **Conflict detection** | `Scheduler.detect_conflicts()` finds every pair of scheduled tasks whose time windows overlap. `get_conflict_warnings()` formats the results as plain-English warnings shown at the top of the plan. |
| **Skipped task explanation** | Tasks that don't fit are listed below the plan with the reason (`could not fit within daily time budget`). |
| **Scheduling reasoning** | Each scheduled task shows a plain-English explanation: why that priority, whether the preferred time was matched, and category-specific notes (e.g. "medications must stay on schedule"). |
| **Recurring task support** | `Task.next_occurrence()` generates a fresh task copy due the next day (DAILY) or next week (WEEKLY). `Pet.mark_task_complete()` marks a task done and auto-appends the follow-up so the pet's list stays current. |
| **Mark tasks complete** | In the Tasks tab, any pending task can be marked completed from a dropdown. |
| **Multi-pet support** | An owner can have multiple pets; each pet has its own task list and the scheduler targets one pet per run. |

---

## 📸 Demo

<a href="/demo images/pawpal_screenshot.png" target="_blank"><img src='/demo images/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## Project Structure

```
pawpal_system.py   # All domain classes: Owner, Pet, Task, Scheduler, DailyPlan
app.py             # Streamlit UI — connects directly to backend
tests/
  test_pawpal.py   # 22 automated tests covering scheduling behaviors
uml_final.md       # Final class + sequence diagrams (Mermaid.js)
uml_design.md      # Original design-phase diagram
reflection.md      # Design choices, tradeoffs, and AI collaboration notes
```

---

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

<<<<<<< HEAD
```bash
streamlit run app.py
```

### Run the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

---

## Testing Coverage

| Test class | Behaviors verified |
|---|---|
| `TestTaskCompletion` | `mark_complete()`, `mark_skipped()`, `reset()` flip `TaskStatus` correctly |
| `TestTaskAddition` | `Pet.add_task()` appends tasks; multiple adds work correctly |
| `TestSortingCorrectness` | Priority sort returns CRITICAL → HIGH → LOW; time-sensitive tasks outrank equal-priority peers; `sort_by_time()` returns chronological order; both handle empty lists |
| `TestRecurrenceLogic` | DAILY spawns next-day task; WEEKLY spawns next-week task; ONCE returns `None`; `mark_task_complete()` auto-appends follow-up; follow-ups get fresh `id` and `PENDING` status |
| `TestConflictDetection` | Overlapping windows detected; back-to-back tasks not flagged; `get_conflict_warnings()` returns readable strings; single-task schedule never conflicts; scheduler's own slot assignment produces no internal conflicts |

**Confidence: 4 / 5** — core scheduling logic is thoroughly covered (22 passing tests). One star withheld because the WEEKLY recurrence filter uses a hardcoded Mon/Wed/Fri heuristic and the Streamlit UI has no automated tests.
=======
1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
>>>>>>> 1c73efec1bde1b57e0a4227cdf21261b86357f26
