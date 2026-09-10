# In-class drills

**This file documents how the drills are designed. The papers themselves are not here.**

This repository is public. Drill questions and answers live in the private instructor
repository (`../../../itcs355-instructor-private/drills/`), which has no git remote. Section A
is concept questions, and a student who reads them beforehand is sitting a different exam.

> **Exposure on record.** `drill-05.md` was committed here on 6 September 2026 with its model
> answers and was publicly readable until removed. Removal does not undo publication. Treat
> Drill 5's Section A as burned and rewrite those three questions before the final week.

Five drills, 3 marks each, 15 marks total. One at the start of each session, 15 minutes,
closed-book except for the student's own repository.

## The shape, and why

Each drill is **half concepts, half evidence**.

| | Marks | Drawn from | Purpose |
|---|---|---|---|
| Section A — concepts | 1.5 | the previous session | did they understand it |
| Section B — evidence | 1.5 | **their own lab submission** | did they do it themselves |

Section B is the anti-copying mechanism and it is the reason the drills exist at all. The
questions cannot be answered from a borrowed repository, because they ask for numbers and
decisions that are specific to the student's own submission: their p95, their run ID, the
permission they removed, the case in their golden set that failed. A student who cloned a
friend's lab can pass Section A and will fail Section B.

This means **Section B has to be prepared per student**, from their submitted repository,
before the session. Budget 2 minutes per student. It is the cost of the mechanism, and it is
lower than the cost of not being able to tell who did the work.

## Marking

Half a mark per question, six questions. No partial credit within a question — the answers
are short and specific enough that they are right or they are not. Mark during the debrief
slot that follows; do not carry a stack of drills home.

## Status

All five papers are written and live in the private instructor repository, alongside
student-facing question papers for LMS upload.

| Drill | Held at start of | Covers |
|---|---|---|
| 1 | Session 2 | Session 1 + Lab 1 — reproducibility, containers, data versioning |
| 2 | Session 3 | Session 2 + Lab 2 — tracking, registries, lineage |
| 3 | Session 4 | Session 3 + Lab 3 — serving, latency, release safety |
| 4 | Session 5 | Session 4 + Lab 4 — testing, drift, incident response |
| 5 | Final week | Session 5 + Lab 5 — LLM operations, IAM, cost |
