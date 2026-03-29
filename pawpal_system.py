"""
PawPal+ — Backend Logic Layer
All domain classes and scheduling engine live here.
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import uuid
from datetime import datetime, timedelta


# ── Enumerations ──────────────────────────────────────────────────────────────

class Priority(Enum):
    """Urgency level used to rank tasks during scheduling."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskCategory(Enum):
    """The type of care activity a task represents."""
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"
    APPOINTMENT = "appointment"
    VET_CHECKUP = "vet_checkup"


class RecurrencePattern(Enum):
    """How often a task repeats across days."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class TaskStatus(Enum):
    """Lifecycle state of a single task instance."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ── Task ──────────────────────────────────────────────────────────────────────

@dataclass
class Task:
    """A single pet-care activity with its scheduling metadata."""

    title: str
    category: TaskCategory
    duration_minutes: int
    priority: Priority
    recurrence: RecurrencePattern = RecurrencePattern.DAILY
    notes: str = ""
    preferred_time_of_day: str = ""   # e.g. "morning", "evening"
    is_time_sensitive: bool = False
    due_date: Optional[str] = None            # "YYYY-MM-DD"; set automatically on recurrence
    status: TaskStatus = field(default=TaskStatus.PENDING, init=False)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8], init=False)

    def priority_score(self) -> int:
        """Return a numeric sort key; time-sensitive tasks gain +1 to beat same-priority peers."""
        base = self.priority.value          # LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4
        bonus = 1 if self.is_time_sensitive else 0
        return base * 10 + bonus            # e.g. CRITICAL time-sensitive → 41

    def mark_complete(self) -> None:
        """Set status to COMPLETED."""
        self.status = TaskStatus.COMPLETED

    def mark_skipped(self) -> None:
        """Set status to SKIPPED."""
        self.status = TaskStatus.SKIPPED

    def reset(self) -> None:
        """Reset status back to PENDING."""
        self.status = TaskStatus.PENDING

    def next_occurrence(self, from_date: str) -> Optional["Task"]:
        """Return a fresh Task copy due on the next scheduled date, or None if non-recurring.

        Args:
            from_date: The completion date in 'YYYY-MM-DD' format used as the
                       reference point for calculating the next due date.

        Returns:
            A new Task with a reset status/id and an updated due_date, or None
            if this task's recurrence is ONCE or CUSTOM.
        """
        if self.recurrence == RecurrencePattern.DAILY:
            delta = timedelta(days=1)
        elif self.recurrence == RecurrencePattern.WEEKLY:
            delta = timedelta(weeks=1)
        else:
            return None

        try:
            next_date = datetime.strptime(from_date, "%Y-%m-%d").date() + delta
        except ValueError:
            return None

        return Task(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
            notes=self.notes,
            preferred_time_of_day=self.preferred_time_of_day,
            is_time_sensitive=self.is_time_sensitive,
            due_date=next_date.isoformat(),
        )

    def __repr__(self) -> str:
        return (
            f"Task('{self.title}', {self.category.value}, "
            f"{self.duration_minutes}min, priority={self.priority.name}, "
            f"status={self.status.name})"
        )


# ── Pet ───────────────────────────────────────────────────────────────────────

@dataclass
class Pet:
    """A pet profile that owns a list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age_years: float = 0.0
    weight_kg: float = 0.0
    tasks: List[Task] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8], init=False)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id. Return True if found and removed."""
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted highest priority first."""
        return sorted(self.tasks, key=lambda t: t.priority_score(), reverse=True)

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Return all tasks matching the given category."""
        return [t for t in self.tasks if t.category == category]

    def mark_task_complete(self, task: Task, today: str) -> Optional[Task]:
        """Mark a task complete and, if recurring, auto-add its next occurrence.

        Args:
            task:  The Task instance belonging to this pet to mark complete.
            today: Today's date as 'YYYY-MM-DD', used to compute the next due date.

        Returns:
            The newly created follow-up Task if one was added, otherwise None.
        """
        task.mark_complete()
        next_task = task.next_occurrence(today)
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def get_total_duration(self) -> int:
        """Return the sum of all task durations in minutes."""
        return sum(t.duration_minutes for t in self.tasks)

    def __repr__(self) -> str:
        return (
            f"Pet('{self.name}', {self.species}, "
            f"{len(self.tasks)} task(s), total={self.get_total_duration()}min)"
        )


# ── Owner ─────────────────────────────────────────────────────────────────────

@dataclass
class Owner:
    """A pet owner with a daily time budget and one or more pets."""

    name: str
    email: str = ""
    available_minutes_per_day: int = 120
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8], init=False)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by id. Return True if found and removed."""
        for i, p in enumerate(self.pets):
            if p.id == pet_id:
                self.pets.pop(i)
                return True
        return False

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all pets; the Scheduler's single entry point."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_total_task_minutes(self) -> int:
        """Return combined task minutes across all pets."""
        return sum(p.get_total_duration() for p in self.pets)

    def __repr__(self) -> str:
        return (
            f"Owner('{self.name}', {len(self.pets)} pet(s), "
            f"available={self.available_minutes_per_day}min/day)"
        )


# ── ScheduledTask ─────────────────────────────────────────────────────────────

@dataclass
class ScheduledTask:
    """A Task paired with a concrete start/end time slot and scheduling reasoning."""

    task: Task
    start_time: str   # "HH:MM" 24-hour format
    end_time: str     # "HH:MM" 24-hour format
    reasoning: str = ""

    def to_dict(self) -> dict:
        """Serialize to a plain dict (for Streamlit tables / JSON export)."""
        return {
            "title": self.task.title,
            "category": self.task.category.value,
            "priority": self.task.priority.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.task.duration_minutes,
            "reasoning": self.reasoning,
        }


# ── DailyPlan ─────────────────────────────────────────────────────────────────

@dataclass
class DailyPlan:
    """The output of a scheduling run: ordered tasks, skipped tasks, and a summary."""

    date: str          # "YYYY-MM-DD"
    owner: Owner
    pet: Pet
    available_minutes: int
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    plan_summary: str = ""

    @property
    def total_scheduled_minutes(self) -> int:
        """Sum of durations for all scheduled tasks."""
        return sum(st.task.duration_minutes for st in self.scheduled_tasks)

    def add_scheduled_task(self, st: ScheduledTask) -> None:
        """Append a ScheduledTask to the plan and mark the task as scheduled."""
        st.task.status = TaskStatus.SCHEDULED
        self.scheduled_tasks.append(st)

    def add_skipped_task(self, task: Task) -> None:
        """Record a task that could not be fit into the day."""
        task.mark_skipped()
        self.skipped_tasks.append(task)

    def get_utilization_pct(self) -> float:
        """Return scheduled minutes / available minutes as a percentage."""
        if self.available_minutes == 0:
            return 0.0
        return round(self.total_scheduled_minutes / self.available_minutes * 100, 1)

    def display(self) -> None:
        """Print a human-readable schedule to stdout (used by demo.py)."""
        print(f"\n{'='*55}")
        print(f"  PawPal+ Daily Plan  |  {self.date}")
        print(f"  Owner : {self.owner.name}   |   Pet: {self.pet.name}")
        print(f"{'='*55}")

        if not self.scheduled_tasks:
            print("  No tasks scheduled.")
        else:
            for st in self.scheduled_tasks:
                print(
                    f"  {st.start_time} - {st.end_time}  "
                    f"[{st.task.priority.name:<8}]  {st.task.title}"
                )
                print(f"             -> {st.reasoning}")

        if self.skipped_tasks:
            print(f"\n  Skipped ({len(self.skipped_tasks)}):")
            for t in self.skipped_tasks:
                print(f"    - {t.title} - {t.notes or 'time budget exceeded'}")

        print(f"\n  Scheduled : {self.total_scheduled_minutes} min")
        print(f"  Available : {self.available_minutes} min")
        print(f"  Utilization: {self.get_utilization_pct()}%")
        if self.plan_summary:
            print(f"\n  Summary: {self.plan_summary}")
        print(f"{'='*55}\n")

    def to_dict(self) -> dict:
        """Serialize the full plan to a dict (for Streamlit / JSON export)."""
        return {
            "date": self.date,
            "owner": self.owner.name,
            "pet": self.pet.name,
            "available_minutes": self.available_minutes,
            "total_scheduled_minutes": self.total_scheduled_minutes,
            "utilization_pct": self.get_utilization_pct(),
            "scheduled_tasks": [st.to_dict() for st in self.scheduled_tasks],
            "skipped_tasks": [t.title for t in self.skipped_tasks],
            "plan_summary": self.plan_summary,
        }


# ── Scheduler ─────────────────────────────────────────────────────────────────

class Scheduler:
    """Scheduling engine that retrieves tasks from an Owner and produces a DailyPlan."""

    def __init__(
        self,
        owner: Owner,
        pet: Pet,
        day_start_hour: int = 7,
        day_start_minute: int = 0,
        day_end_hour: int = 21,
    ) -> None:
        self.owner = owner
        self.pet = pet
        self.day_start_hour = day_start_hour
        self.day_start_minute = day_start_minute
        self.day_end_hour = day_end_hour

    # ── helpers ───────────────────────────────────────────────────────────────

    def _minutes_to_hhmm(self, minutes_from_midnight: int) -> str:
        """Convert an offset in minutes from midnight to 'HH:MM' string."""
        h, m = divmod(minutes_from_midnight, 60)
        return f"{h:02d}:{m:02d}"

    def _day_capacity(self) -> int:
        """Total schedulable minutes between day start time and day_end_hour."""
        return self.day_end_hour * 60 - (self.day_start_hour * 60 + self.day_start_minute)

    # ── public API ────────────────────────────────────────────────────────────

    def generate_daily_plan(self, date: str) -> DailyPlan:
        """Ask the Owner for all tasks, filter by pet and date, sort by priority, slot into the day, and return a DailyPlan."""
        # 1. Retrieve every task the owner knows about, then narrow to this pet
        all_owner_tasks = self.owner.get_all_tasks()
        pet_tasks = [t for t in all_owner_tasks if t in self.pet.tasks]

        # 2. Filter by recurrence / date
        candidate_tasks = self._filter_recurring(pet_tasks, date)

        # 3. Sort highest priority first
        sorted_tasks = self.sort_tasks_by_priority(candidate_tasks)

        # 4. Slot into the day
        scheduled, skipped = self._assign_time_slots(sorted_tasks)

        # 5. Build plan
        budget = min(self.owner.available_minutes_per_day, self._day_capacity())
        plan = DailyPlan(
            date=date,
            owner=self.owner,
            pet=self.pet,
            available_minutes=budget,
        )
        for st in scheduled:
            plan.add_scheduled_task(st)
        for t in skipped:
            plan.add_skipped_task(t)

        plan.plan_summary = self._build_summary(plan)
        return plan

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return a new list sorted by priority_score() descending."""
        return sorted(tasks, key=lambda t: t.priority_score(), reverse=True)

    def detect_conflicts(self, scheduled: List[ScheduledTask]) -> List[Tuple[ScheduledTask, ScheduledTask]]:
        """Return all (a, b) pairs of ScheduledTasks whose time windows overlap."""
        conflicts = []
        for i in range(len(scheduled)):
            for j in range(i + 1, len(scheduled)):
                a, b = scheduled[i], scheduled[j]
                # Parse HH:MM into comparable integers (minutes from midnight)
                a_start = self._hhmm_to_minutes(a.start_time)
                a_end   = self._hhmm_to_minutes(a.end_time)
                b_start = self._hhmm_to_minutes(b.start_time)
                b_end   = self._hhmm_to_minutes(b.end_time)
                # Overlap when neither is entirely before the other
                if a_start < b_end and b_start < a_end:
                    conflicts.append((a, b))
        return conflicts

    def sort_by_time(self, scheduled_tasks: List[ScheduledTask]) -> List[ScheduledTask]:
        """Return a new list of ScheduledTasks sorted by start_time ascending.

        Uses a lambda on the 'HH:MM' string directly — zero-padded 24-hour
        strings compare correctly in lexicographic order, so no parsing needed.

        Args:
            scheduled_tasks: Any list of ScheduledTask objects.

        Returns:
            A new list sorted earliest-to-latest by start_time.
        """
        return sorted(scheduled_tasks, key=lambda st: st.start_time)

    def filter_by_status(self, tasks: List[Task], status: TaskStatus) -> List[Task]:
        """Return only the tasks whose status matches the given TaskStatus.

        Args:
            tasks:  A flat list of Task objects to filter.
            status: The TaskStatus value to match (e.g. TaskStatus.COMPLETED).

        Returns:
            A filtered list containing only tasks with the requested status.
        """
        return [t for t in tasks if t.status == status]

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return all tasks belonging to the pet with the given name.

        The lookup is case-insensitive.  Searches across every pet registered
        with this Scheduler's owner.

        Args:
            pet_name: The pet's name (case-insensitive).

        Returns:
            The matching pet's task list, or an empty list if no pet matches.
        """
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                return list(pet.tasks)
        return []

    def get_conflict_warnings(self, scheduled: List[ScheduledTask]) -> List[str]:
        """Return human-readable warning strings for every overlapping task pair.

        Wraps detect_conflicts() and formats each conflicting pair as a plain
        warning message instead of raising an exception — the caller can simply
        print or log the results.

        Args:
            scheduled: The list of ScheduledTask objects to inspect.

        Returns:
            A list of warning strings (empty if no conflicts exist).
        """
        warnings: List[str] = []
        for a, b in self.detect_conflicts(scheduled):
            warnings.append(
                f"  WARNING: '{a.task.title}' ({a.start_time}–{a.end_time}) "
                f"conflicts with '{b.task.title}' ({b.start_time}–{b.end_time})"
            )
        return warnings

    def fits_in_window(self, task: Task, used_minutes: int) -> bool:
        """Return True if adding this task keeps total time within the owner's daily budget."""
        budget = min(self.owner.available_minutes_per_day, self._day_capacity())
        return used_minutes + task.duration_minutes <= budget

    def build_reasoning(self, task: Task, slot: str) -> str:
        """Return a plain-English explanation of why this task was scheduled at the given slot."""
        reasons = []

        priority_labels = {
            Priority.CRITICAL: "Critical priority - must not be skipped",
            Priority.HIGH:     "High priority",
            Priority.MEDIUM:   "Medium priority",
            Priority.LOW:      "Low priority - scheduled because time allows",
        }
        reasons.append(priority_labels[task.priority])

        if task.is_time_sensitive:
            reasons.append("time-sensitive so placed as early as possible")

        if task.preferred_time_of_day:
            hour = int(slot.split(":")[0])
            actual = self._hour_to_period(hour)
            if actual == task.preferred_time_of_day.lower():
                reasons.append(f"matches preferred time ({task.preferred_time_of_day})")
            else:
                reasons.append(
                    f"preferred {task.preferred_time_of_day} but "
                    f"scheduled {actual} due to earlier tasks"
                )

        category_notes = {
            TaskCategory.MEDICATION:  "medications must stay on schedule",
            TaskCategory.FEEDING:     "regular feeding maintains healthy digestion",
            TaskCategory.WALK:        "daily exercise supports physical health",
            TaskCategory.GROOMING:    "grooming keeps coat and skin healthy",
            TaskCategory.ENRICHMENT:  "mental stimulation prevents boredom",
            TaskCategory.APPOINTMENT: "appointment has a fixed external time",
            TaskCategory.VET_CHECKUP: "vet visit - high importance",
        }
        if task.category in category_notes:
            reasons.append(category_notes[task.category])

        return "; ".join(reasons) + f" | slot: {slot}"

    # ── private helpers ───────────────────────────────────────────────────────

    def _assign_time_slots(
        self, sorted_tasks: List[Task]
    ) -> Tuple[List[ScheduledTask], List[Task]]:
        """Walk priority-sorted tasks and assign sequential HH:MM slots, splitting into (scheduled, skipped)."""
        scheduled: List[ScheduledTask] = []
        skipped:   List[Task]          = []

        # Cursor in minutes from midnight
        cursor = self.day_start_hour * 60 + self.day_start_minute
        used   = 0

        for task in sorted_tasks:
            if self.fits_in_window(task, used):
                start_str = self._minutes_to_hhmm(cursor)
                end_str   = self._minutes_to_hhmm(cursor + task.duration_minutes)
                reasoning = self.build_reasoning(task, start_str)
                scheduled.append(
                    ScheduledTask(
                        task=task,
                        start_time=start_str,
                        end_time=end_str,
                        reasoning=reasoning,
                    )
                )
                cursor += task.duration_minutes
                used   += task.duration_minutes
            else:
                if not task.notes:
                    task.notes = "could not fit within daily time budget"
                skipped.append(task)

        return scheduled, skipped

    def _filter_recurring(self, tasks: List[Task], date: str) -> List[Task]:
        """Return tasks whose recurrence pattern includes the given date (ONCE/DAILY always pass; WEEKLY checks day-of-week)."""
        try:
            target = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            # If date is unparseable, include everything rather than silently drop
            return list(tasks)

        result = []
        for task in tasks:
            if task.recurrence in (RecurrencePattern.ONCE,
                                   RecurrencePattern.DAILY,
                                   RecurrencePattern.CUSTOM):
                result.append(task)
            elif task.recurrence == RecurrencePattern.WEEKLY:
                # Include on the same day-of-week as today (Mon=0 … Sun=6)
                # This is a simple heuristic; a real app would store a start date
                if target.weekday() in (0, 2, 4):   # Mon / Wed / Fri by default
                    result.append(task)
        return result

    def _hhmm_to_minutes(self, hhmm: str) -> int:
        """Convert 'HH:MM' string to integer minutes from midnight."""
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    def _hour_to_period(self, hour: int) -> str:
        """Map a 24-hour clock hour to a named period of day."""
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 21:
            return "evening"
        return "night"

    def _build_summary(self, plan: DailyPlan) -> str:
        """One-sentence summary attached to the finished DailyPlan."""
        n_sched  = len(plan.scheduled_tasks)
        n_skip   = len(plan.skipped_tasks)
        util     = plan.get_utilization_pct()
        msg = (
            f"Scheduled {n_sched} task(s) using {plan.total_scheduled_minutes} "
            f"of {plan.available_minutes} available minutes ({util}% utilization)"
        )
        if n_skip:
            msg += f"; {n_skip} task(s) skipped due to time budget."
        else:
            msg += "."
        return msg
