# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML included four core classes: `Owner`, `Pet`, `Task`, and a `Scheduler`. `Owner` held the daily time budget and a list of pets; `Pet` owned the task list; `Task` carried the priority, duration, and category fields; and `Scheduler` was responsible for filtering and slotting tasks into a day.

I also included four enumerations — `Priority`, `TaskCategory`, `RecurrencePattern`, and `TaskStatus` — from the start because I knew tasks would need clear categorical values rather than raw strings to make sorting and filtering reliable.

**b. Design changes**

The biggest structural change was the introduction of `ScheduledTask` and `DailyPlan`. In the initial sketch, the scheduler returned a plain list of tasks. During implementation I realized the UI needed concrete start/end times and a reasoning string for each task, and it needed a summary object that tracked skipped tasks separately. Splitting this into two classes kept `Task` as a pure data object and gave the UI a single structured result to render.

I also added `Task.next_occurrence()` and `Pet.mark_task_complete()` after realizing the recurrence feature required more than a simple status flip — it needed to automatically spawn a new task instance so the pet's schedule stayed populated across days. That logic belonged on the domain objects, not in the Scheduler or the UI.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Time budget** — `Owner.available_minutes_per_day` caps the total minutes the scheduler will assign. Tasks that exceed the budget are skipped.
2. **Priority** — `Task.priority_score()` combines the `Priority` enum value (1–4) with a time-sensitivity bonus (+1). Higher scores are scheduled first, so CRITICAL and HIGH tasks always claim the available budget before MEDIUM or LOW ones.
3. **Recurrence** — `_filter_recurring()` restricts which tasks are candidates for a given date. DAILY and ONCE tasks always qualify; WEEKLY tasks pass only on Mon/Wed/Fri (a deliberate simplification).

The time budget was prioritized as the hardest constraint because it maps directly to the owner's real-world capacity. Priority and recurrence are soft in the sense that they influence ordering and eligibility but don't override the budget ceiling.

**b. Tradeoffs**

The conflict-detection algorithm checks only for **exact time-slot overlap** between two tasks — it flags a conflict when one task's window intersects another's (start A < end B and start B < end A). It does **not** reason about transitions between tasks; two tasks scheduled back-to-back with no travel or prep buffer would pass even if they are practically impossible to execute sequentially.

This is a reasonable tradeoff for the current scenario because the scheduler assigns tasks sequentially without intentional gaps, so back-to-back is the intended normal state. Detecting exact overlaps catches the most dangerous scheduling bugs while avoiding false positives that would overwhelm an owner with warnings for a legitimately dense schedule. A more sophisticated implementation could track transition time per task category (e.g., travel to the dog park), but that would require additional data the model does not currently collect.

---

## 3. AI Collaboration

**a. How you used AI**

I used VS Code Copilot across all phases:

- **Design phase:** Chat helped me think through whether `ScheduledTask` should be a separate class or a named tuple. Asking "what are the tradeoffs between a dataclass and a named tuple for a scheduling result?" surfaced the idea that a dataclass makes it easier to add methods later — that pushed me toward `@dataclass`.
- **Implementation:** Inline completions sped up the repetitive parts of the codebase (enum definitions, `__repr__` methods, dataclass field declarations). Copilot's suggestions were almost always correct for the pattern but I reviewed each one.
- **Debugging:** When `generate_daily_plan()` was returning an empty schedule, I pasted the method into chat and asked it to trace the data flow. It caught that I was filtering `owner.get_all_tasks()` against `self.pet.tasks` using `in` (object identity), which worked in practice but would silently break if tasks were ever copied. I addressed this in the design.
- **Test writing:** I used `#file:pawpal_system.py` + "generate unit tests for the conflict detection logic" to scaffold the test class, then rewrote each test to match my actual method signatures and add edge cases (single-task schedule, back-to-back non-overlapping tasks) the generated tests missed.

The most effective prompting pattern was giving Copilot specific scope: `#file:pawpal_system.py — only look at the Scheduler class` rather than asking open-ended questions. Focused context produced suggestions that were much closer to usable.

**b. Judgment and verification**

When generating the test suite, Copilot suggested testing `detect_conflicts()` by passing raw `Task` objects rather than `ScheduledTask` objects. The method signature takes `List[ScheduledTask]`, not `List[Task]`, so those tests would have raised a `TypeError` at runtime rather than actually testing the behavior.

I rejected this because the test would pass the wrong type, fail to exercise the overlap logic, and give a false sense of coverage. I rewrote the tests to construct proper `ScheduledTask` instances with explicit `start_time` and `end_time` strings, then verified the overlap math by hand for each case (overlapping, back-to-back, identical windows) before trusting the test results.

This was the clearest reminder that AI-generated tests need the same scrutiny as AI-generated implementation code. The suggestion wasn't wrong about *what* to test; it was wrong about the type contract, which is exactly the kind of subtle error that automated generation misses without domain context.

---

## 4. Testing and Verification

**a. What you tested**

Five test classes covering 22 behaviors:

- `TestTaskCompletion` — status transitions (`mark_complete`, `mark_skipped`, `reset`)
- `TestTaskAddition` — `Pet.add_task()` and list integrity
- `TestSortingCorrectness` — priority sort order, time-sensitivity tiebreaking, chronological `sort_by_time()`, empty-list safety
- `TestRecurrenceLogic` — DAILY/WEEKLY follow-up generation, `Pet.mark_task_complete()` auto-append, ONCE returning None, fresh id/status on follow-ups
- `TestConflictDetection` — overlap detection, back-to-back non-conflict, readable warning strings, single-task safety, internal consistency of the scheduler's own slot assignment

These were the most important behaviors to test because they are the behaviors with the most failure modes: sorting can silently return the wrong order, recurrence can create duplicate tasks or miss the next date, and conflict detection can produce false positives or miss real overlaps depending on how boundary conditions are handled.

**b. Confidence**

**4 / 5 stars.** All 22 tests pass and cover the critical scheduling path end-to-end. The one-star gap is from two known gaps: the WEEKLY recurrence heuristic (hardcoded to Mon/Wed/Fri) is not tested against a real start-date, and the Streamlit UI layer has no automated tests — only manual verification. If I had more time I would add parametrized tests for the WEEKLY filter across all seven weekdays and use Streamlit's `AppTest` framework to verify that the budget warning and conflict banners render under the right conditions.

---

## 5. Reflection

**a. What went well**

The separation between `pawpal_system.py` and `app.py` worked very well. Because all logic lived in the backend module, I could test the scheduling engine completely independently of Streamlit, run the CLI demo to verify output, and add UI features without touching any algorithmic code. The boundary also made it easy to reason about where a bug lived — if the plan was wrong it was a backend issue; if the display was wrong it was a UI issue.

**b. What you would improve**

The WEEKLY recurrence logic is the most obvious thing to redesign. Right now it uses a Mon/Wed/Fri heuristic because tasks don't store a start date. A proper fix would add an `Optional[str] start_date` to `Task` and compute recurrence relative to that anchor, which would make weekly tasks behave correctly regardless of when in the week the app is opened.

I would also add a progress bar or Gantt-style timeline view in the Streamlit UI so the owner can visually scan the day at a glance rather than reading a card list.

**c. Key takeaway**

The most important lesson from this project is that **AI tools shift the bottleneck from writing to deciding.** Copilot could generate a `Scheduler` class in seconds, but it couldn't decide whether conflicts should be warnings or errors, whether skipped tasks deserved their own section, or whether time-sensitivity should be a priority tiebreaker or a separate sort key. Every time I accepted a suggestion, I was making an implicit architectural decision. The sessions where I was most effective were the ones where I already had a clear mental model — I used AI to fill in the boilerplate and surface alternatives, not to design the system from scratch. Being the "lead architect" means knowing enough about what you're building that you can evaluate AI suggestions critically rather than accepting them because they compile.
