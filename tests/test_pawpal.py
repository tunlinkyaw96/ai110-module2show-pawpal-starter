"""
PawPal+ — Automated Test Suite
Run with:  pytest tests/test_pawpal.py -v
"""

import pytest
from pawpal_system import (
    Task, Pet, TaskCategory, Priority, TaskStatus, RecurrencePattern,
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
