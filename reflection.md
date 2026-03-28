# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict-detection algorithm checks only for **exact time-slot overlap** between two tasks — it flags a conflict when one task's window intersects another's (start A < end B and start B < end A). It does **not** reason about task durations in a continuous timeline; a 5-minute medication at 08:00 and a 30-minute walk that starts at 08:04 would be caught, but two tasks scheduled back-to-back with no travel or prep time between them would silently pass even though they may be practically impossible.

This is a reasonable tradeoff for the current scenario because the scheduler assigns tasks sequentially without gaps, so back-to-back is the intended normal state. Detecting exact overlaps catches the most dangerous bugs (tasks accidentally placed at the same clock time), while avoiding false positives that would overwhelm an owner with warnings for a legitimately dense schedule. A more sophisticated implementation could track transition time between tasks (e.g., travel to the dog park), but that requires additional data the model does not currently collect.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
