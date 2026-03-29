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

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

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
