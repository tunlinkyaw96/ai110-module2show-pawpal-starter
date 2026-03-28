"""
PawPal+ — Automated Test Suite
Run with:  pytest tests/test_pawpal.py -v
"""

import pytest
from pawpal_system import (
    Task, Pet, Owner, Scheduler, ScheduledTask,
    TaskCategory, Priority, TaskStatus, RecurrencePattern,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_task():
    """A fresh PENDING task reused across tests."""
    return Task(
        title="Morning Walk",
        category=TaskCategory.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
    )


@pytest.fixture
def sample_pet():
    """An empty pet reused across tests."""
    return Pet(name="Mochi", species="dog")


# ── Test 1: Task Completion ───────────────────────────────────────────────────

class TestTaskCompletion:

    def test_mark_complete_changes_status(self, sample_task):
        """mark_complete() must flip status from PENDING to COMPLETED."""
        assert sample_task.status == TaskStatus.PENDING   # starts pending
        sample_task.mark_complete()
        assert sample_task.status == TaskStatus.COMPLETED

    def test_mark_skipped_changes_status(self, sample_task):
        """mark_skipped() must flip status from PENDING to SKIPPED."""
        sample_task.mark_skipped()
        assert sample_task.status == TaskStatus.SKIPPED

    def test_reset_restores_pending(self, sample_task):
        """reset() must return a completed task back to PENDING."""
        sample_task.mark_complete()
        sample_task.reset()
        assert sample_task.status == TaskStatus.PENDING


# ── Test 2: Task Addition ─────────────────────────────────────────────────────

class TestTaskAddition:

    def test_add_task_increases_count(self, sample_pet, sample_task):
        """Adding one task must increase the pet's task count by exactly 1."""
        before = len(sample_pet.tasks)
        sample_pet.add_task(sample_task)
        assert len(sample_pet.tasks) == before + 1

    def test_added_task_is_retrievable(self, sample_pet, sample_task):
        """The added task must appear in the pet's task list."""
        sample_pet.add_task(sample_task)
        assert sample_task in sample_pet.tasks

    def test_add_multiple_tasks(self, sample_pet):
        """Adding three tasks must result in exactly three tasks on the pet."""
        for title in ("Breakfast", "Medication", "Grooming"):
            sample_pet.add_task(
                Task(title, TaskCategory.FEEDING, 10, Priority.MEDIUM)
            )
        assert len(sample_pet.tasks) == 3


# ── Fixtures shared by scheduling tests ───────────────────────────────────────

@pytest.fixture
def basic_owner_pet():
    """An Owner with one Pet, ready for Scheduler use."""
    pet = Pet(name="Biscuit", species="dog")
    owner = Owner(name="Alex", available_minutes_per_day=120)
    owner.add_pet(pet)
    return owner, pet


# ── Test 3: Sorting Correctness ───────────────────────────────────────────────

class TestSortingCorrectness:

    def test_tasks_returned_highest_priority_first(self, basic_owner_pet):
        """sort_tasks_by_priority() must return tasks in descending priority order."""
        owner, pet = basic_owner_pet
        low  = Task("Low Task",      TaskCategory.ENRICHMENT, 10, Priority.LOW)
        high = Task("High Task",     TaskCategory.WALK,        20, Priority.HIGH)
        crit = Task("Critical Task", TaskCategory.MEDICATION,  5,  Priority.CRITICAL)
        pet.add_task(low)
        pet.add_task(high)
        pet.add_task(crit)

        scheduler = Scheduler(owner, pet)
        sorted_tasks = scheduler.sort_tasks_by_priority(pet.tasks)

        assert sorted_tasks[0].priority == Priority.CRITICAL
        assert sorted_tasks[1].priority == Priority.HIGH
        assert sorted_tasks[2].priority == Priority.LOW

    def test_time_sensitive_beats_same_priority(self):
        """A time-sensitive task must rank above a non-time-sensitive task of equal priority."""
        normal = Task("Normal High",    TaskCategory.WALK,     20, Priority.HIGH,
                      is_time_sensitive=False)
        urgent = Task("Urgent High",    TaskCategory.WALK,     20, Priority.HIGH,
                      is_time_sensitive=True)

        assert urgent.priority_score() > normal.priority_score()

    def test_scheduled_tasks_in_chronological_order(self, basic_owner_pet):
        """sort_by_time() must return ScheduledTasks with start_time ascending."""
        owner, pet = basic_owner_pet
        scheduler = Scheduler(owner, pet)

        # Build manually ordered ScheduledTasks out-of-order
        task_a = Task("Task A", TaskCategory.WALK,    10, Priority.LOW)
        task_b = Task("Task B", TaskCategory.FEEDING, 10, Priority.LOW)
        task_c = Task("Task C", TaskCategory.GROOMING, 10, Priority.LOW)
        st_a = ScheduledTask(task_a, start_time="14:00", end_time="14:10")
        st_b = ScheduledTask(task_b, start_time="08:00", end_time="08:10")
        st_c = ScheduledTask(task_c, start_time="11:00", end_time="11:10")

        result = scheduler.sort_by_time([st_a, st_b, st_c])
        times = [st.start_time for st in result]
        assert times == ["08:00", "11:00", "14:00"]

    def test_empty_task_list_sorts_to_empty(self, basic_owner_pet):
        """Sorting an empty list must return an empty list without error."""
        owner, pet = basic_owner_pet
        scheduler = Scheduler(owner, pet)
        assert scheduler.sort_tasks_by_priority([]) == []
        assert scheduler.sort_by_time([]) == []


# ── Test 4: Recurrence Logic ──────────────────────────────────────────────────

class TestRecurrenceLogic:

    def test_daily_task_creates_next_day_occurrence(self):
        """next_occurrence() on a DAILY task must return a task due the following day."""
        task = Task(
            "Evening Feed", TaskCategory.FEEDING, 15, Priority.HIGH,
            recurrence=RecurrencePattern.DAILY, due_date="2026-03-27"
        )
        next_task = task.next_occurrence("2026-03-27")

        assert next_task is not None
        assert next_task.due_date == "2026-03-28"

    def test_weekly_task_creates_next_week_occurrence(self):
        """next_occurrence() on a WEEKLY task must return a task due 7 days later."""
        task = Task(
            "Bath Day", TaskCategory.GROOMING, 30, Priority.MEDIUM,
            recurrence=RecurrencePattern.WEEKLY, due_date="2026-03-27"
        )
        next_task = task.next_occurrence("2026-03-27")

        assert next_task is not None
        assert next_task.due_date == "2026-04-03"

    def test_once_task_returns_none(self):
        """next_occurrence() on a ONCE task must return None (no follow-up)."""
        task = Task(
            "Vet Visit", TaskCategory.VET_CHECKUP, 60, Priority.CRITICAL,
            recurrence=RecurrencePattern.ONCE
        )
        assert task.next_occurrence("2026-03-27") is None

    def test_mark_task_complete_adds_follow_up(self):
        """Pet.mark_task_complete() must append the next occurrence to the pet's task list."""
        pet = Pet(name="Mochi", species="cat")
        task = Task(
            "Morning Meal", TaskCategory.FEEDING, 10, Priority.HIGH,
            recurrence=RecurrencePattern.DAILY
        )
        pet.add_task(task)
        assert len(pet.tasks) == 1

        pet.mark_task_complete(task, "2026-03-27")

        # Original task completed, new follow-up added
        assert task.status == TaskStatus.COMPLETED
        assert len(pet.tasks) == 2
        assert pet.tasks[1].due_date == "2026-03-28"

    def test_next_occurrence_has_fresh_id_and_pending_status(self):
        """The follow-up task must get a new id and start as PENDING."""
        task = Task(
            "Walkies", TaskCategory.WALK, 30, Priority.HIGH,
            recurrence=RecurrencePattern.DAILY
        )
        next_task = task.next_occurrence("2026-03-27")

        assert next_task is not None
        assert next_task.id != task.id
        assert next_task.status == TaskStatus.PENDING

    def test_pet_with_no_tasks_mark_complete_raises_no_error(self):
        """Completing a task on an empty pet should not crash the system."""
        pet = Pet(name="Ghost", species="cat")
        task = Task("Solo Task", TaskCategory.ENRICHMENT, 10, Priority.LOW,
                    recurrence=RecurrencePattern.ONCE)
        pet.add_task(task)
        # Should not raise
        result = pet.mark_task_complete(task, "2026-03-27")
        assert result is None  # ONCE tasks produce no follow-up


# ── Test 5: Conflict Detection ────────────────────────────────────────────────

class TestConflictDetection:

    def _make_st(self, title, start, end):
        """Helper to build a ScheduledTask without a full scheduler."""
        task = Task(title, TaskCategory.WALK, 30, Priority.LOW)
        return ScheduledTask(task=task, start_time=start, end_time=end)

    def test_overlapping_tasks_flagged_as_conflict(self, basic_owner_pet):
        """Two tasks sharing a time window must appear in detect_conflicts()."""
        owner, pet = basic_owner_pet
        scheduler = Scheduler(owner, pet)

        st_a = self._make_st("Task A", "09:00", "09:30")
        st_b = self._make_st("Task B", "09:15", "09:45")  # overlaps A

        conflicts = scheduler.detect_conflicts([st_a, st_b])
        assert len(conflicts) == 1
        assert (st_a, st_b) in conflicts

    def test_non_overlapping_tasks_have_no_conflicts(self, basic_owner_pet):
        """Back-to-back tasks that do not overlap must not be flagged."""
        owner, pet = basic_owner_pet
        scheduler = Scheduler(owner, pet)

        st_a = self._make_st("Task A", "09:00", "09:30")
        st_b = self._make_st("Task B", "09:30", "10:00")  # starts exactly when A ends

        conflicts = scheduler.detect_conflicts([st_a, st_b])
        assert conflicts == []

    def test_conflict_warnings_returns_strings(self, basic_owner_pet):
        """get_conflict_warnings() must return a non-empty list of strings for overlapping tasks."""
        owner, pet = basic_owner_pet
        scheduler = Scheduler(owner, pet)

        st_a = self._make_st("Walk",      "10:00", "10:30")
        st_b = self._make_st("Grooming",  "10:20", "11:00")

        warnings = scheduler.get_conflict_warnings([st_a, st_b])
        assert len(warnings) >= 1
        assert isinstance(warnings[0], str)
        assert "WARNING" in warnings[0]

    def test_no_conflicts_returns_empty_warnings(self, basic_owner_pet):
        """get_conflict_warnings() must return an empty list when there are no conflicts."""
        owner, pet = basic_owner_pet
        scheduler = Scheduler(owner, pet)

        st_a = self._make_st("Morning Walk", "07:00", "07:30")
        st_b = self._make_st("Afternoon Fed", "13:00", "13:20")

        warnings = scheduler.get_conflict_warnings([st_a, st_b])
        assert warnings == []

    def test_single_task_has_no_conflicts(self, basic_owner_pet):
        """A schedule with only one task can never conflict with itself."""
        owner, pet = basic_owner_pet
        scheduler = Scheduler(owner, pet)

        st_a = self._make_st("Only Task", "08:00", "08:45")
        assert scheduler.detect_conflicts([st_a]) == []

    def test_generate_daily_plan_produces_no_internal_conflicts(self, basic_owner_pet):
        """The Scheduler's own slot assignment must not create overlapping tasks."""
        owner, pet = basic_owner_pet
        for title, cat, dur, pri in [
            ("Walk",        TaskCategory.WALK,      30, Priority.HIGH),
            ("Breakfast",   TaskCategory.FEEDING,   10, Priority.CRITICAL),
            ("Grooming",    TaskCategory.GROOMING,  20, Priority.MEDIUM),
        ]:
            pet.add_task(Task(title, cat, dur, pri))

        scheduler = Scheduler(owner, pet)
        plan = scheduler.generate_daily_plan("2026-03-27")
        conflicts = scheduler.detect_conflicts(plan.scheduled_tasks)
        assert conflicts == [], f"Unexpected conflicts in generated plan: {conflicts}"
