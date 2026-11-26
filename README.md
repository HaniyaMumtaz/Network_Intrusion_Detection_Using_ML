# Network Intrusion Detection System (NSL-KDD + Random Forest)

A machine learning prototype that classifies network connections as **normal** or **attack**, with a simple web interface.
Built for the **Programming for Artificial Intelligence** major team project (CUSIT, Fall 2026).

> **Prototype only.** This is a classroom project trained on old, simulated data. It supports human review and must **not** be used to block traffic or make real security decisions.

---

## 1. Project overview

| | |
|---|---|
| **Problem** | Network administrators cannot inspect thousands of connection records by hand. |
| **Stakeholder** | IT / network administrator of a small or medium organisation (for example a campus or small company). |
| **Task** | Binary classification: `0` = normal connection, `1` = attack. |
| **Dataset** | NSL-KDD (125,973 training records, 22,544 official test records). |
| **Models** | Decision Tree (baseline) and Random Forest (improved), built with scikit-learn. |
| **Interface** | Gradio web app with three tabs (single connection, file upload, random real example). |
| **Final model** | Random Forest, 100 trees (Experiment 2). |

## 2. Team

| Member | Roll no. | Role |
|---|---|---|
| Haniya | 16000 | Coding: data loading and cleaning, EDA, models, evaluation, GUI, tests |
| Saba | 17407 | Documentation: proposal, README, final report |
| Samrina | 15966 | Presentation slides and demo preparation |

Course coordinator: Syed Muhammad Mohuddin. 

## 3. Repository structure

```
.
├── README.md                     this file
├── requirements.txt              Python libraries
├── .gitignore
├── notebooks/
│   └── NSL_KDD_dataset_audit_modern.ipynb   main notebook: audit, cleaning, EDA, models, GUI
├── src/
│   └── nids_core.py              reusable functions (load, clean, pipeline, safe prediction)
├── tests/
│   └── test_nids_core.py         27 automated unit tests
├── data/
│   ├── raw/                      KDDTrain+.txt, KDDTest+.txt (download, see Section 4)
│   └── processed/                train_cleaned.csv, test_cleaned.csv (made by the notebook)
├── docs/
│   ├── TESTING.md                test plan, results, errors found and fixed
│   ├── PROJECT_LOG.md            meeting record, decisions, task record
│   ├── CONTRIBUTION_MATRIX.md    who did what
│   └── PRESENTATION_AND_VIVA_GUIDE.md
├── reports/                      proposal, dataset audit, final report
└── slides/                       presentation slides
```

## 4. Dataset

- **Name:** NSL-KDD, created by M. Tavallaee, E. Bagheri, W. Lu and A. A. Ghorbani (University of New Brunswick, 2009), a cleaned version of the KDD Cup 1999 data.
- **Copy used:** Zenodo record `10.5281/zenodo.17424143` (https://zenodo.org/records/17424143), licence **CC BY 4.0**.
- **Files:** `KDDTrain+.txt` (train) and `KDDTest+.txt` (official test). Put them in `data/raw/`.
- **Access date:** [add the date you downloaded the files]

Things to know about these files:

- They are **tab-separated** and have **no header row**; the code adds the 43 column names.
- The test file has an **empty `difficulty` column**, **3 duplicate rows**, and only the labels `Normal` / `Attack` (the training file has 22 attack names). Cleaning handles all three.
- There is no personal or identifiable information in the data.

## 5. How to run

### Option A: Google Colab (recommended)

1. Open the notebook in Colab (Colab > File > Open notebook > GitHub tab, or upload the `.ipynb`).
2. Put the two dataset files in Google Drive (for example `MyDrive/KDDTrain+.txt`) or upload them to Colab, and set `TRAIN_PATH` and `TEST_PATH` in the path cell to match.
3. Choose **Runtime > Restart and run all** (or run the cells from top to bottom).
4. The last cell starts the GUI and prints a public link. Open it in your browser.

### Option B: on your own computer

```bash
git clone <repository-url>
cd <repository-folder>
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
jupyter notebook notebooks/NSL_KDD_dataset_audit_modern.ipynb
```

Skip the Google Drive mount cell and point `TRAIN_PATH` / `TEST_PATH` to `data/raw/`.

### Run the automated tests

```bash
python -m unittest discover -s tests -v
```

The tests use small fake data, so no dataset is needed. Expected result: `Ran 27 tests ... OK`.

## 6. What the notebook does

1. **Load** the tab-separated files and add column names.
2. **Audit** missing values, duplicates, class balance and categories.
3. **Clean:** drop `difficulty`, tidy text and labels, force numbers, remove missing, duplicate and negative rows, create the target and attack family, remove constant columns (leaves 40 features).
4. **Explore** the data with four visualisations.
5. **Split** the training file 80/20 (stratified, seed 42). The official test file is used only for final reporting. The encoder is inside the pipeline, so there is no data leakage.
6. **Train and evaluate** three experiments.
7. **Test** edge cases (missing column, new category, empty file, text in a number column).
8. **Save** the final model (`nids_random_forest.joblib`) and the cleaned data.
9. **Launch the GUI.**

## 7. Results

| Experiment | Data | Accuracy | Precision | Recall | F1 | False positive rate |
|---|---|---|---|---|---|---|
| Exp 1: Decision Tree | validation | 99.85% | 99.81% | 99.86% | 99.83% | 0.16% |
| Exp 1: Decision Tree | official test | 79.02% | 91.78% | 69.35% | 79.01% | 8.21% |
| Exp 2: Random Forest | validation | 99.90% | 99.95% | 99.85% | 99.90% | 0.04% |
| Exp 2: Random Forest | official test | 78.14% | 96.92% | 63.62% | 76.82% | 2.67% |
| Exp 3: Random Forest (balanced) | validation | 99.89% | 99.96% | 99.81% | 99.88% | 0.04% |
| Exp 3: Random Forest (balanced) | official test | 76.12% | 96.69% | 60.10% | 74.13% | 2.72% |

**Reading the results**

- All models are almost perfect on the **validation split**, so it cannot tell them apart.
- On the **official test file** (different traffic mix) performance drops sharply: the final Random Forest catches **63.6%** of attacks with **2.7%** false alarms.
- The Decision Tree catches more attacks (69.4%) but raises more false alarms (8.2%). The Random Forest is more cautious.
- The success criteria (recall of at least 90% with at most 5% false alarms; +3 points F1 over the baseline) were **not** met on the official test file, and the +3 points F1 criterion was not met on validation either. The full discussion is in the final report.

## 8. GUI

The Gradio app has three tabs:

1. **Check one connection:** choose protocol, service and flag, enter bytes and connection count, or press a preset (normal web browsing, SYN flood, ICMP smurf flood).
2. **Check a file:** upload a `.txt` or `.csv` file with the NSL-KDD columns (with or without a header) and get a summary and a table of the 500 highest-risk rows.
3. **Random real example:** compares the model's answer with the true label for a random validation record.

Each result shows the **attack probability** and an **alert level**: High (90% or more), Medium (50% to 90%), Low (below 50%).

> **Privacy note:** the notebook launches the GUI with a public share link (`share=True`). Do not upload real organisational network logs to it.

## 9. Testing

Details are in [`docs/TESTING.md`](docs/TESTING.md). In short:

- the official test file is never used for training or tuning;
- 4 edge cases are tested in the notebook;
- 27 automated unit tests cover loading, cleaning, the pipeline, safe prediction and file reading;
- the errors found during development and their fixes are recorded.

## 10. Limitations and ethics

- NSL-KDD is based on **1999 simulated traffic**: no modern attacks, and results may not transfer to a real network.
- Some attack types are very rare (R2L and U2R are under 1% of the data).
- The test file has a different traffic mix, which is the main reason for the large gap between validation and test results.
- Errors by service or protocol were not analysed, so fairness across traffic types is unchecked.
- The alert thresholds (50% and 90%) were chosen by the team and not tuned.
- No personal data is used or stored.

## 11. Future work

Cost-sensitive threshold tuning to raise recall, a leave-one-attack-family-out experiment, an attack-family classifier, per-alert explanations, and repeating the experiments on a newer dataset such as UNSW-NB15.

## 12. References

1. M. Tavallaee, E. Bagheri, W. Lu and A. A. Ghorbani, "A detailed analysis of the KDD CUP 99 data set," *IEEE CISDA*, 2009. doi: 10.1109/CISDA.2009.5356528
2. Saad, "NSL-KDD Dataset," version 1, Zenodo, 2025. doi: 10.5281/zenodo.17424143
3. L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5-32, 2001.
4. F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *JMLR*, vol. 12, pp. 2825-2830, 2011.
5. A. Abid et al., "Gradio: Hassle-free sharing and testing of ML models in the wild," arXiv:1906.02569, 2019.

The complete reference list is in the final report.

