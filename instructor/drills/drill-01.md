# Drill 1 — From Notebook to Reproducible ML

**3 marks · 15 minutes · start of Session 2 · CLO1 3**

Covers Session 1 and Lab 1. Closed-book except for the student's own repository, which they
will need for Section B.

Section B must be prepared per student from their submitted Lab 1 before the session — see
[`README.md`](README.md). The bracketed fields below are filled in from their repository.

---

## Section A — concepts (1.5 marks)

### A1 · 0.5 · CLO1

> Your `Dockerfile` says `FROM python:3.11-slim`. Nothing in your repository changes. You build
> in September and again in November, and the second build reports a different metric.
>
> Name the mechanism, and give the one-line fix.

**Model answer.** The **tag moved**. `python:3.11-slim` is a pointer, not an identity — it names
different bytes in November than it did in September, and a rebuilt base can change libc or a
maths library underneath an otherwise pinned Python. Fix: pin by digest,
`FROM python:3.11-slim@sha256:...`.

**Full marks** require the idea that the tag itself is not a fixed thing. "Docker changed" or
"the image updated" earns nothing — the point is that *they chose* a moving reference and could
have chosen a fixed one.

### A2 · 0.5 · CLO1

> In the notebook we opened Session 1 with, splitting the rows at random instead of splitting by
> machine raised the reported AUC by about **0.20**.
>
> What was the model actually doing, and why is the higher number the worse outcome?

**Model answer.** Every machine contributes 25 readings, the label belongs to the machine, and
the features describe the machine. Splitting row-wise puts the same machine on both sides, so the
model **recognises machines it has already seen** rather than predicting failure.

The higher number is worse because it estimates performance on a task that never occurs: in
production every machine is one the model has not seen. The 0.20 is not skill, it is a measurement
error that flatters you — and it would have been discovered by the ops team, not by you.

**Full marks require both halves.** "It memorised the training data" alone is half an answer; the
second half — that the estimate answers the wrong question — is the part that matters.

### A3 · 0.5 · CLO1

> A week later, with no change to your repository, `make reproduce` gives a different number.
>
> Name **two** of the four links that could be loose, and for each, the one check that would tell
> you it was that one.

**Model answer.** Any two of:

| Link | The check |
|---|---|
| **Data** | compare the data fingerprint / DVC hash against the one in the tracked run |
| **Environment** | the lock file is unhashed, or was not used — diff installed versions against it |
| **Image** | the base was tag-pinned, not digest-pinned — compare the image digest |
| **Randomness** | the seed was not set or not logged — check the run's `seed` parameter |

**Full marks** need a *check*, not just a name. "It could be the data" is not an answer; "the
fingerprint would differ from the one logged with the run" is.

---

## Section B — evidence (1.5 marks)

From the student's own submission. They may open their repository.

### B1 · 0.5 · CLO1

> Read out your data fingerprint. Name one thing that would change it, and one thing that would
> not.

**Marking.** Full marks for the value plus a correct pair — *would* change it: regenerating with
a different seed, adding rows, editing a value. *Would not*: renaming the file, re-running the
same generation, committing other code. Zero if they cannot find the fingerprint, which means
nothing in their pipeline is recording it.

### B2 · 0.5 · CLO1

> Across your five tracked runs you varied **[parameter]**. What did it do to validation, and did
> the test score move the same way?

**Marking.** Full marks for a direction and a rough magnitude from their own runs. Watch for the
student whose five runs differ only by seed — the handout forbids it explicitly, so it is worth
naming in the debrief. Watch also for validation and test moving in opposite directions and the
student not having noticed; that is Session 2's material arriving early, and worth a mark.

### B3 · 0.5 · CLO1

> Your README says that under time pressure you would drop **[hashes / the digest pin / seeds]**
> first. What specifically breaks when you do?

**Marking.** Full marks for a concrete consequence of *their own* stated choice, not a general
defence of pinning. Any of the three is defensible; refusing to choose is not, and the handout
says so. A student who wrote the answer and cannot now explain it did not write it.

---

## Marking summary

| | Topic | CLO | Marks |
|---|---|---|---|
| A1 | Tags move; digests do not | CLO1 | 0.5 |
| A2 | Group leakage, and why a higher score is worse | CLO1 | 0.5 |
| A3 | Diagnosing which of the four links is loose | CLO1 | 0.5 |
| B1 | Their data fingerprint, and what moves it | CLO1 | 0.5 |
| B2 | What their own study actually showed | CLO1 | 0.5 |
| B3 | Their own reproducibility trade-off | CLO1 | 0.5 |
| | **Total** | **CLO1 3** | **3** |

Matches the Drill 1 row on the *Assessment Blueprint* sheet.

## Not asked, deliberately

`RUBRIC-lab1.md` also suggests *"your stated tolerance and how you chose it"*. **Do not ask it
this term.** The Lab 1 README currently tells students to derive the tolerance from the spread
across seeds, but `make reproduce` pins `--seed`, so that instruction produces a tolerance far
looser than the evidence supports. A student who followed the handout would be penalised for
following the handout. Fix the guidance first, then this becomes a good question.

## Wrong answers worth expecting

| Answer | Why it scores nothing |
|---|---|
| A1: "Docker updated the image" | Passive. They chose a moving reference; the fix is theirs |
| A2: "It overfitted" | Overfitting is a training-set phenomenon; this is a *measurement* error |
| A2: "The higher score is fine, it's just optimistic" | It answers a question production never asks |
| A3: "Check if anything changed" | The whole skill is knowing *which* check separates the four |
| B1: cannot locate a fingerprint | Nothing in their pipeline records what data produced the number |
| B2: five runs differing only by seed | The handout forbids it in writing |

## Running it

Fifteen minutes on paper or in the LMS, before the Lab 1 debrief — the drill primes the debrief,
so do not reorder them. Mark during the debrief; six short answers is about three minutes each.

A2 is the bridge into the debrief. If the room does well on it, run the debrief faster and spend
the time on the container failures instead.
