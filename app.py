"""
PawPal+ — Streamlit UI
Connects directly to the backend classes in pawpal_system.py.
"""

# ── Step 1: Import backend classes ────────────────────────────────────────────
import streamlit as st
from datetime import date

from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    TaskCategory, Priority, RecurrencePattern,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Smart pet care planning — powered by your backend logic.")
st.divider()

# ── Step 2: Session-state initialisation ─────────────────────────────────────
# st.session_state acts like a persistent dictionary that survives re-runs.
# We check "owner" in st.session_state BEFORE creating anything so the object
# is only created once per browser session, not on every page refresh.

if "owner" not in st.session_state:
    st.session_state.owner = None          # set to an Owner instance on setup

if "active_pet_name" not in st.session_state:
    st.session_state.active_pet_name = None

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_owner, tab_tasks, tab_schedule = st.tabs(
    ["1  Owner & Pets", "2  Tasks", "3  Daily Schedule"]
)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Owner & Pets
# ═══════════════════════════════════════════════════════════════════════════════
with tab_owner:

    # ── Owner form ────────────────────────────────────────────────────────────
    st.subheader("Owner Profile")

    with st.form("owner_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            owner_name  = st.text_input("Your name", value="Jordan")
            owner_email = st.text_input("Email (optional)", value="")
        with col_b:
            daily_budget = st.slider(
                "Daily time available (minutes)", 30, 480,
                value=120, step=10,
                help="How many minutes per day can you spend on pet care?",
            )

        save_owner = st.form_submit_button("Save Owner Profile")

    if save_owner:
        # Create a new Owner OR update the existing one's fields
        if st.session_state.owner is None:
            # First save: build the Owner object and store it in session_state
            st.session_state.owner = Owner(
                name=owner_name,
                email=owner_email,
                available_minutes_per_day=daily_budget,
            )
        else:
            # Subsequent saves: update fields in-place (preserves existing pets)
            st.session_state.owner.name = owner_name
            st.session_state.owner.email = owner_email
            st.session_state.owner.available_minutes_per_day = daily_budget
        st.success(f"Owner profile saved — {owner_name}, {daily_budget} min/day.")

    if st.session_state.owner is None:
        st.info("Fill in your profile above to get started.")
        st.stop()   # nothing else can render until an owner exists

    owner: Owner = st.session_state.owner   # typed alias for IDE help below

    # ── Add a pet ─────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Add a Pet")

    with st.form("add_pet_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            pet_name    = st.text_input("Pet name", value="Mochi")
            pet_species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
        with col2:
            pet_breed   = st.text_input("Breed (optional)")
            pet_age     = st.number_input("Age (years)", min_value=0.0, max_value=30.0,
                                          value=2.0, step=0.5)

        add_pet_btn = st.form_submit_button("Add Pet")

    if add_pet_btn:
        # Prevent duplicates by checking existing names
        existing_names = [p.name.lower() for p in owner.pets]
        if pet_name.lower() in existing_names:
            st.warning(f"A pet named '{pet_name}' already exists.")
        else:
            new_pet = Pet(name=pet_name, species=pet_species,
                          breed=pet_breed, age_years=pet_age)
            owner.add_pet(new_pet)          # Owner.add_pet() wires the object graph
            st.session_state.active_pet_name = new_pet.name
            st.success(f"Added {pet_name} the {pet_species}!")

    # ── Pet roster ────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Your Pets")

    if not owner.pets:
        st.info("No pets yet — add one above.")
    else:
        for pet in owner.pets:
            with st.expander(f"**{pet.name}** — {pet.species}  |  {len(pet.tasks)} task(s)"):
                col_x, col_y, col_z = st.columns(3)
                col_x.metric("Species",  pet.species.capitalize())
                col_y.metric("Age",      f"{pet.age_years} yr")
                col_z.metric("Tasks",    len(pet.tasks))

                if st.button(f"Remove {pet.name}", key=f"remove_{pet.id}"):
                    owner.remove_pet(pet.id)   # Owner.remove_pet() handles list cleanup
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Tasks
# ═══════════════════════════════════════════════════════════════════════════════
with tab_tasks:

    if st.session_state.owner is None or not st.session_state.owner.pets:
        st.info("Set up an owner profile and add at least one pet first.")
        st.stop()

    owner: Owner = st.session_state.owner

    # ── Pet selector ──────────────────────────────────────────────────────────
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names, key="task_pet_selector")
    selected_pet: Pet = next(p for p in owner.pets if p.name == selected_pet_name)

    st.subheader(f"Add a Task for {selected_pet.name}")

    # ── Add-task form ─────────────────────────────────────────────────────────
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_title    = st.text_input("Task title", value="Morning walk")
            task_category = st.selectbox(
                "Category",
                options=[c.value for c in TaskCategory],
            )
            task_priority = st.selectbox(
                "Priority",
                options=[p.name for p in Priority],
                index=2,   # default: HIGH
            )
        with col2:
            task_duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
            task_recurrence = st.selectbox(
                "Recurrence",
                options=[r.value for r in RecurrencePattern],
                index=1,   # default: daily
            )
            task_preferred = st.selectbox(
                "Preferred time of day",
                options=["", "morning", "afternoon", "evening"],
            )

        col3, col4 = st.columns(2)
        with col3:
            task_sensitive = st.checkbox("Time-sensitive?")
        with col4:
            task_notes = st.text_input("Notes (optional)")

        add_task_btn = st.form_submit_button("Add Task")

    if add_task_btn:
        new_task = Task(
            title=task_title,
            category=TaskCategory(task_category),       # str → enum
            duration_minutes=int(task_duration),
            priority=Priority[task_priority],            # name → enum
            recurrence=RecurrencePattern(task_recurrence),
            preferred_time_of_day=task_preferred,
            is_time_sensitive=task_sensitive,
            notes=task_notes,
        )
        selected_pet.add_task(new_task)   # Pet.add_task() attaches it to the pet
        st.success(f"Added '{task_title}' to {selected_pet.name}.")
        st.rerun()

    # ── Current task list ─────────────────────────────────────────────────────
    st.divider()
    st.subheader(f"{selected_pet.name}'s Tasks")

    if not selected_pet.tasks:
        st.info("No tasks yet — add one above.")
    else:
        # Show sorted by priority so the table mirrors scheduler order
        sorted_tasks = selected_pet.get_tasks_by_priority()
        rows = [
            {
                "Title":    t.title,
                "Category": t.category.value,
                "Priority": t.priority.name,
                "Duration": f"{t.duration_minutes} min",
                "Recurrence": t.recurrence.value,
                "Time-sensitive": "yes" if t.is_time_sensitive else "no",
            }
            for t in sorted_tasks
        ]
        st.dataframe(rows, use_container_width=True)

        st.caption(
            f"Total task time: **{selected_pet.get_total_duration()} min** "
            f"| Owner budget: **{owner.available_minutes_per_day} min/day**"
        )

        # Remove individual tasks
        with st.expander("Remove a task"):
            task_to_remove = st.selectbox(
                "Select task to remove",
                options=[t.title for t in selected_pet.tasks],
                key="remove_task_select",
            )
            if st.button("Remove task"):
                task_obj = next(t for t in selected_pet.tasks if t.title == task_to_remove)
                selected_pet.remove_task(task_obj.id)   # Pet.remove_task() by id
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Daily Schedule
# ═══════════════════════════════════════════════════════════════════════════════
with tab_schedule:

    if st.session_state.owner is None or not st.session_state.owner.pets:
        st.info("Set up an owner profile and add at least one pet first.")
        st.stop()

    owner: Owner = st.session_state.owner

    st.subheader("Generate Daily Schedule")

    # ── Controls ──────────────────────────────────────────────────────────────
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        sched_pet_name = st.selectbox(
            "Pet", [p.name for p in owner.pets], key="sched_pet_selector"
        )
    with col_s2:
        plan_date = st.date_input("Date", value=date.today())
    with col_s3:
        start_hour = st.number_input("Day starts (hour)", min_value=4, max_value=12,
                                     value=7, step=1)

    sched_pet: Pet = next(p for p in owner.pets if p.name == sched_pet_name)

    if not sched_pet.tasks:
        st.warning(f"{sched_pet.name} has no tasks yet. Add tasks in the Tasks tab first.")
        st.stop()

    if st.button("Generate Schedule", type="primary"):

        # ── Step 3: wire UI action to Scheduler method ────────────────────────
        scheduler = Scheduler(
            owner=owner,
            pet=sched_pet,
            day_start_hour=start_hour,
            day_end_hour=22,
        )
        plan = scheduler.generate_daily_plan(plan_date.isoformat())

        # ── Display the plan ──────────────────────────────────────────────────
        st.success(plan.plan_summary)

        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Scheduled tasks",  len(plan.scheduled_tasks))
        m2.metric("Skipped tasks",    len(plan.skipped_tasks))
        m3.metric("Minutes used",     plan.total_scheduled_minutes)
        m4.metric("Utilization",      f"{plan.get_utilization_pct()}%")

        st.divider()

        # Scheduled tasks table
        if plan.scheduled_tasks:
            st.subheader("Today's Plan")
            for st_task in plan.scheduled_tasks:
                with st.container(border=True):
                    left, right = st.columns([3, 1])
                    with left:
                        st.markdown(
                            f"**{st_task.start_time} - {st_task.end_time}** "
                            f"&nbsp;&nbsp; {st_task.task.title}"
                        )
                        st.caption(f"Why: {st_task.reasoning}")
                    with right:
                        priority_color = {
                            "CRITICAL": "🔴",
                            "HIGH":     "🟠",
                            "MEDIUM":   "🟡",
                            "LOW":      "🟢",
                        }
                        badge = priority_color.get(st_task.task.priority.name, "⚪")
                        st.markdown(f"{badge} **{st_task.task.priority.name}**")
                        st.caption(f"{st_task.task.duration_minutes} min")
        else:
            st.info("No tasks could be scheduled — try increasing the daily time budget.")

        # Skipped tasks
        if plan.skipped_tasks:
            st.divider()
            st.subheader("Skipped")
            for t in plan.skipped_tasks:
                st.warning(
                    f"**{t.title}** ({t.duration_minutes} min) — "
                    f"{t.notes or 'exceeded daily time budget'}"
                )

        # Conflict report
        conflicts = scheduler.detect_conflicts(plan.scheduled_tasks)
        if conflicts:
            st.divider()
            st.error(f"{len(conflicts)} scheduling conflict(s) detected:")
            for a, b in conflicts:
                st.write(f"- {a.task.title} overlaps with {b.task.title}")
