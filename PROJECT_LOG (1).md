# Project Log and Task Record

Team: **Haniya (16000)**, **Saba (17407)**, **Samrina (15994)**
Project: Network Intrusion Detection System (NSL-KDD + Random Forest)

> **How to use this file.** The assignment asks for a short project log / meeting record. It must describe what really happened. The tables below are pre-filled with the decisions and work that the project involved, but **you must add the real dates and attendees, and delete or correct any line that does not match what your team actually did.** Do not invent meetings.


| Decision | Reason |
|---|---|
| Domain: Cybersecurity (network intrusion detection) | On the approved domain list; public benchmark data available |
| Dataset: NSL-KDD from Zenodo (CC BY 4.0) | Small, tabular, labelled, duplicates removed, well documented |
| Binary target (normal = 0, attack = 1) | Matches the stakeholder question; attack families are too rare to predict reliably |
| Official test file used only for final reporting | Avoids data leakage and gives an honest estimate |
| Final model: Random Forest, 100 trees (Exp 2) | Best validation scores and a false positive rate under 5%; most reliable alerts |
| Interface: Gradio in Colab | Quick to build, shareable link for the demo |
| Tests: notebook edge cases plus `unittest` suite | Satisfies the testing requirement and makes the code reproducible |

## 3. Roles

| Member | Role |
|---|---|
| Haniya | Coding / ML development (data cleaning, EDA, models, evaluation, GUI, tests) |
| Saba | Project lead and documentation (proposal, README, final report, test documentation) |
| Samrina | Presentation and demo preparation (slides) |

For a 3-member team the Git/QA role is combined with the other roles, as the assignment allows.

## 4. Task and issue record

Create one **GitHub Issue** for each task (Issues tab > New issue), assign it to its owner, and close it when it is done. This table is the plan; the Issues tab is the evidence.

| Milestone | Task | Owner | Status |
|---|---|---|---|
| 1 | Research 5+ sources and write the proposal | Saba | Done |
| 2 | Compare two datasets and write the dataset audit and data dictionary | Haniya (checks), Saba (write-up) | Done |
| 3 | Create repository, folders, README, requirements | Haniya, Saba | [update] |
| 3 | Load-data function and reusable module | Haniya | Done |
| 4 | Cleaning function and cleaning report | Haniya | Done |
| 4 | Four EDA visualisations with interpretations | Haniya (charts), Saba (text) | Done / [update] |
| 5 | Baseline Decision Tree and metrics | Haniya | Done |
| 6 | Random Forest experiments and results table | Haniya | Done |
| 7 | Edge-case tests and unit tests | Haniya | Done |
| 7 | Test documentation (`docs/TESTING.md`) | Saba | [update] |
| 7 | GUI (Gradio, three tabs) | Haniya | Done |
| 8 | Final report (8 to 12 pages) | Saba | [update] |
| 8 | Presentation slides (8 to 10) | Samrina | [update] |
| 8 | Demo rehearsal and backup recording | All | [update] |
| 8 | Contribution matrix and this log | Saba | [update] |
| 8 | Viva preparation (every member) | All | [update] |

## 5. Problems met 

Wrong file separator, empty `difficulty` column and mismatched labels in the test file, duplicate rows, variable name errors, dataset path error, and the GUI library not being installed. Each was fixed and recorded.

## 6. Before final submission 

- [ ] Notebook re-run from top to bottom with **Runtime > Restart and run all**, with no errors, and saved with outputs.
- [ ] Old test cells and duplicate path cells removed from the notebook.
- [ ] Every member has commits from their own GitHub account (`git shortlog -sn`).
- [ ] GitHub Issues created and closed.
- [ ] Screenshots of the GUI, results and commit history added to the report and `docs/images/`.
- [ ] Report placeholders (highlighted yellow) all filled in.
- [ ] Slides finished and a backup recording of the demo made.
- [ ] Every member can explain the whole project.
