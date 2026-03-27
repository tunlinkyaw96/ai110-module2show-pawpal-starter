"""
PawPal+ — Backend Logic Layer
All domain classes and scheduling engine live here.
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import uuid


# ── Enumerations ──────────────────────────────────────────────────────────────

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskCategory(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"
    APPOINTMENT = "appointment"
    VET_CHECKUP = "vet_checkup"


class RecurrencePattern(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class TaskStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    SKIPPED = "skipped"


# ── Task ──────────────────────────────────────────────────────────────────────

@dataclass
class Task:
    title: str
    category: TaskCategory
    duration_minutes: int
    priority: Priority
    recurrence: RecurrencePattern = RecurrencePattern.DAILY
    notes: str = ""
    preferred_time_of_day: str = ""   # e.g. "morning", "evening"
    is_time_sensitive: bool = False
    status: TaskStatus = field(default=TaskStatus.PENDING, init=False)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8], init=False)

    def priority_score(self) -> int:
        """Return a numeric score for sorting (higher = more urgent)."""
        pass

    def mark_complete(self) -> None:
        """Set status to COMPLETED."""
        pass

    def mark_skipped(self) -> None:
        """Set status to SKIPPED."""
        pass

    def reset(self) -> None:
        """Reset status back to PENDING."""
        pass

    def __repr__(self) -> str:
        pass


# ── Pet ───────────────────────────────────────────────────────────────────────

@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age_years: float = 0.0
    weight_kg: float = 0.0
    tasks: List[Task] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8], init=False)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        pass

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id. Return True if found and removed."""
        pass

    def get_tasks_by_priority(self) -> List[Task]:
        """Return tasks sorted highest priority first."""
        pass

    def get_tasks_by_category(self, category: TaskCategory) -> List[Task]:
        """Return all tasks matching the given category."""
        pass

    def get_total_duration(self) -> int:
        """Return the sum of all task durations in minutes."""
        pass

    def __repr__(self) -> str:
        pass


# ── Owner ─────────────────────────────────────────────────────────────────────

@dataclass
class Owner:
    name: str
    email: str = ""
    available_minutes_per_day: int = 120
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8], init=False)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        pass

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by id. Return True if found and removed."""
        pass

    def get_total_task_minutes(self) -> int:
        """Return combined task minutes across all pets."""
        pass

    def __repr__(self) -> str:
        pass


# ── ScheduledTask ─────────────────────────────────────────────────────────────

@dataclass
class ScheduledTask:
    task: Task
    start_time: str   # "HH:MM" 24-hour format
    end_time: str     # "HH:MM" 24-hour format
    reasoning: str = ""

    def to_dict(self) -> dict:
        """Serialize to a plain dict (for Streamlit tables / JSON export)."""
        pass


# ── DailyPlan ─────────────────────────────────────────────────────────────────

@dataclass
class DailyPlan:
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
        pass

    def add_scheduled_task(self, st: ScheduledTask) -> None:
        """Append a ScheduledTask to the plan."""
        pass

    def add_skipped_task(self, task: Task) -> None:
        """Record a task that could not be fit into the day."""
        pass

    def get_utilization_pct(self) -> float:
        """Return scheduled minutes / available minutes as a percentage."""
        pass

    def display(self) -> None:
        """Print a human-readable schedule to stdout (used by demo.py)."""
        pass

    def to_dict(self) -> dict:
        """Serialize the full plan to a dict (for Streamlit / JSON export)."""
        pass


# ── Scheduler ─────────────────────────────────────────────────────────────────

class Scheduler:
    def __init__(
        self,
        owner: Owner,
        pet: Pet,
        day_start_hour: int = 7,
        day_end_hour: int = 21,
    ) -> None:
        self.owner = owner
        self.pet = pet
        self.day_start_hour = day_start_hour
        self.day_end_hour = day_end_hour

    def generate_daily_plan(self, date: str) -> DailyPlan:
        """
        Main entry point.
        Sort tasks, assign time slots within the owner's available window,
        detect conflicts, and return a complete DailyPlan.
        """
        pass

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return a new list sorted by priority_score() descending."""
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[tuple]:
        """
        Identify tasks whose time windows overlap.
        Return a list of (task_a, task_b) conflict pairs.
        """
        pass

    def fits_in_window(self, task: Task, used_minutes: int) -> bool:
        """
        Return True if adding this task still keeps total scheduled
        time within the owner's available_minutes_per_day.
        """
        pass

    def build_reasoning(self, task: Task, slot: str) -> str:
        """
        Return a human-readable string explaining why this task
        was scheduled at the given time slot.
        """
        pass

    def _assign_time_slots(
        self, sorted_tasks: List[Task]
    ) -> tuple[List[ScheduledTask], List[Task]]:
        """
        Walk through sorted tasks, assign start/end times sequentially,
        and split into (scheduled, skipped) lists.
        """
        pass

    def _filter_recurring(self, tasks: List[Task], date: str) -> List[Task]:
        """
        Return only tasks that should run on the given date
        based on their RecurrencePattern.
        """
        pass
