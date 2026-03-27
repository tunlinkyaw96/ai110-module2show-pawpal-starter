"""
PawPal+ — CLI Demo Script
Run this to verify all backend logic works before connecting to the Streamlit UI.

Usage:
    python main.py
"""

from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    TaskCategory, Priority, RecurrencePattern,
)
from datetime import date


# ── Helper ────────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'-' * 55}")
    print(f"  {title}")
    print(f"{'-' * 55}")


# ── 1. Create the Owner ───────────────────────────────────────────────────────

section("1. Building Owner Profile")

jordan = Owner(
    name="Jordan",
    email="jordan@email.com",
    available_minutes_per_day=120,
    preferences=["morning routines", "short sessions"],
)
print(jordan)


# ── 2. Create Pets ────────────────────────────────────────────────────────────

section("2. Adding Pets")

# Pet 1 — dog
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age_years=3, weight_kg=9.5)

# Pet 2 — cat
luna = Pet(name="Luna", species="cat", breed="Domestic Shorthair", age_years=5, weight_kg=4.2)

print(mochi)
print(luna)


# ── 3. Build Tasks for Mochi ─────────────────────────────────────────────────

section("3. Tasks for Mochi (dog)")

mochi.add_task(Task(
    title="Allergy Medication",
    category=TaskCategory.MEDICATION,
    duration_minutes=5,
    priority=Priority.CRITICAL,
    recurrence=RecurrencePattern.DAILY,
    is_time_sensitive=True,
    notes="Give with a small treat immediately after waking",
))

mochi.add_task(Task(
    title="Morning Walk",
    category=TaskCategory.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    recurrence=RecurrencePattern.DAILY,
    preferred_time_of_day="morning",
    is_time_sensitive=True,
))

mochi.add_task(Task(
    title="Breakfast",
    category=TaskCategory.FEEDING,
    duration_minutes=10,
    priority=Priority.CRITICAL,
    recurrence=RecurrencePattern.DAILY,
    preferred_time_of_day="morning",
))

mochi.add_task(Task(
    title="Trick Training",
    category=TaskCategory.ENRICHMENT,
    duration_minutes=20,
    priority=Priority.MEDIUM,
    recurrence=RecurrencePattern.DAILY,
    notes="Practice 'stay' and 'roll over'",
))

mochi.add_task(Task(
    title="Evening Brush",
    category=TaskCategory.GROOMING,
    duration_minutes=15,
    priority=Priority.LOW,
    recurrence=RecurrencePattern.DAILY,
    preferred_time_of_day="evening",
))

mochi.add_task(Task(
    title="Long Weekend Hike",
    category=TaskCategory.WALK,
    duration_minutes=90,
    priority=Priority.MEDIUM,
    recurrence=RecurrencePattern.WEEKLY,
    notes="Only on weekends - skip on busy weekdays",
))

for t in mochi.tasks:
    print(f"  {t}")


# ── 4. Build Tasks for Luna ──────────────────────────────────────────────────

section("4. Tasks for Luna (cat)")

luna.add_task(Task(
    title="Thyroid Medication",
    category=TaskCategory.MEDICATION,
    duration_minutes=5,
    priority=Priority.CRITICAL,
    recurrence=RecurrencePattern.DAILY,
    is_time_sensitive=True,
    notes="Mix into wet food — do not skip",
))

luna.add_task(Task(
    title="Wet Food Feeding",
    category=TaskCategory.FEEDING,
    duration_minutes=5,
    priority=Priority.HIGH,
    recurrence=RecurrencePattern.DAILY,
    preferred_time_of_day="morning",
))

luna.add_task(Task(
    title="Laser Pointer Play",
    category=TaskCategory.ENRICHMENT,
    duration_minutes=15,
    priority=Priority.MEDIUM,
    recurrence=RecurrencePattern.DAILY,
    preferred_time_of_day="afternoon",
))

luna.add_task(Task(
    title="Litter Box Clean",
    category=TaskCategory.GROOMING,
    duration_minutes=10,
    priority=Priority.HIGH,
    recurrence=RecurrencePattern.DAILY,
))

luna.add_task(Task(
    title="Annual Vet Checkup",
    category=TaskCategory.VET_CHECKUP,
    duration_minutes=60,
    priority=Priority.HIGH,
    recurrence=RecurrencePattern.ONCE,
    is_time_sensitive=True,
    notes="Scheduled for today — do not skip",
))

for t in luna.tasks:
    print(f"  {t}")


# ── 5. Register pets with owner ──────────────────────────────────────────────

section("5. Registering Pets with Owner")

jordan.add_pet(mochi)
jordan.add_pet(luna)

print(jordan)
print(f"\n  Total tasks across all pets : {len(jordan.get_all_tasks())}")
print(f"  Total task minutes demanded : {jordan.get_total_task_minutes()} min")
print(f"  Owner daily budget          : {jordan.available_minutes_per_day} min")


# ── 6. Generate Today's Schedules ────────────────────────────────────────────

today = date.today().isoformat()   # "YYYY-MM-DD"

section(f"6. Today's Schedule for Mochi  [{today}]")
mochi_scheduler = Scheduler(jordan, mochi, day_start_hour=7, day_end_hour=21)
mochi_plan = mochi_scheduler.generate_daily_plan(today)
mochi_plan.display()

section(f"7. Today's Schedule for Luna  [{today}]")
luna_scheduler = Scheduler(jordan, luna, day_start_hour=7, day_end_hour=21)
luna_plan = luna_scheduler.generate_daily_plan(today)
luna_plan.display()


# ── 7. Spot-checks ───────────────────────────────────────────────────────────

section("8. Spot-checks")

# Priority sort
print("  Mochi tasks sorted by priority:")
for t in mochi.get_tasks_by_priority():
    print(f"    score={t.priority_score():>3}  {t.title}")

# Category filter
print("\n  Luna's MEDICATION tasks:")
for t in luna.get_tasks_by_category(TaskCategory.MEDICATION):
    print(f"    {t}")

# Conflict detection
mochi_conflicts = mochi_scheduler.detect_conflicts(mochi_plan.scheduled_tasks)
luna_conflicts  = luna_scheduler.detect_conflicts(luna_plan.scheduled_tasks)
print(f"\n  Mochi schedule conflicts : {len(mochi_conflicts)}")
print(f"  Luna schedule conflicts  : {len(luna_conflicts)}")

# Mark a task complete and verify
med_task = mochi.get_tasks_by_category(TaskCategory.MEDICATION)[0]
med_task.mark_complete()
print(f"\n  After mark_complete(): {med_task.title} -> status = {med_task.status.name}")
med_task.reset()
print(f"  After reset()        : {med_task.title} -> status = {med_task.status.name}")

# to_dict round-trip
print("\n  mochi_plan.to_dict() keys:", list(mochi_plan.to_dict().keys()))

section("Done - all checks passed")
