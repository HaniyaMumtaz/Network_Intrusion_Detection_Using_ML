"""
Core of the NIDS project, taken from the Colab notebook (NSLKDD_main.ipynb).

Everything here is the same logic as the notebook:
  columns, cleaning, train/validation split, one-hot + Random Forest pipeline,
  predict_connections(), the typical-value defaults, the presets,
  the file reader and the HTML result cards.
Only the Gradio screen is replaced by Streamlit (see app.py).
"""
import html as _html
import io

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

RANDOM_STATE = 42          # a fixed number, so the results are the same every time
ATTACK_THRESHOLD = 0.5     # attack probability at or above this = "Attack"

COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count", "serror_rate",
    "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count",
    "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
    "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate", "label", "difficulty",
]
ALL_FEATURES = COLUMNS[:41]
CATEGORICAL = ["protocol_type", "service", "flag"]
NUMERIC_ALL = [c for c in ALL_FEATURES if c not in CATEGORICAL]

FAMILY_MAP = {
    "normal": "Normal",
    "neptune": "DoS", "smurf": "DoS", "back": "DoS", "teardrop": "DoS", "pod": "DoS", "land": "DoS",
    "satan": "Probe", "ipsweep": "Probe", "portsweep": "Probe", "nmap": "Probe",
    "warezclient": "R2L", "guess_passwd": "R2L", "warezmaster": "R2L", "imap": "R2L",
    "ftp_write": "R2L", "multihop": "R2L", "phf": "R2L", "spy": "R2L",
    "buffer_overflow": "U2R", "rootkit": "U2R", "loadmodule": "U2R", "perl": "U2R",
}

# One-click scenarios: protocol, service, flag, src_bytes, dst_bytes, count, serror_rate, logged_in
PRESETS = {
    "normal": ("tcp", "http", "SF", 200, 1000, 5, 0.0, True),
    "syn":    ("tcp", "private", "S0", 0, 0, 300, 1.0, False),
    "smurf":  ("icmp", "ecr_i", "SF", 1032, 0, 500, 0.0, False),
}


# ── Loading and cleaning ─────────────────────────────────────────────────────
def load_data(path):
    """Read one NSL-KDD file (no header) and name its columns."""
    try:
        df = pd.read_csv(path, names=COLUMNS, sep="\t")
        if df["label"].isna().all():
            # some copies of the dataset are comma-separated instead of tab-separated
            df = pd.read_csv(path, names=COLUMNS, sep=",")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}. Check the path.")
    if df["label"].isna().all():
        raise ValueError("All labels are empty: wrong separator or wrong file.")
    return df


def clean_data(df, name):
    """Clean one DataFrame (same steps as the notebook)."""
    print(f"--- Cleaning {name} ---")
    df = df.copy()
    rows_before = len(df)

    df = df.drop(columns=["difficulty"], errors="ignore")

    for col in CATEGORICAL + ["label"]:
        df[col] = df[col].astype(str).str.strip()
    df["label"] = df["label"].str.lower()

    for col in NUMERIC_ALL:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_missing = int(df.isna().any(axis=1).sum())
    print("Rows with missing values removed:", n_missing)
    df = df.dropna()

    n_dup = int(df.duplicated().sum())
    print("Duplicate rows removed:", n_dup)
    df = df.drop_duplicates()

    negative = (df[NUMERIC_ALL] < 0).any(axis=1)
    print("Rows with negative values removed:", int(negative.sum()))
    df = df[~negative]

    df["target"] = (df["label"] != "normal").astype(int)      # 0 = normal, 1 = attack
    df["family"] = df["label"].map(FAMILY_MAP)

    print(f"Rows: {rows_before} -> {len(df)}")
    return df.reset_index(drop=True)


def build_pipeline(model, categorical):
    """Text columns -> numbers (one-hot), then the model."""
    prep = ColumnTransformer(
        [("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical)],
        remainder="passthrough",
    )
    return Pipeline([("prep", prep), ("model", model)])


class Bundle:
    """Everything the app needs after training (replaces the notebook's global variables)."""
    pass


def train_bundle(train_path, test_path):
    """Load, clean, split, train the final model (Experiment 2: Random Forest, 100 trees)."""
    train_raw = load_data(train_path)
    test_raw = load_data(test_path)
    train = clean_data(train_raw, "train")
    test = clean_data(test_raw, "test")

    constant_cols = [c for c in NUMERIC_ALL if train[c].nunique() == 1]
    print("Constant columns removed:", constant_cols)
    train = train.drop(columns=constant_cols)
    test = test.drop(columns=constant_cols)
    numeric = [c for c in NUMERIC_ALL if c not in constant_cols]
    features = CATEGORICAL + numeric

    X_all, y_all = train[features], train["target"]
    X_train, X_val, y_train, y_val = train_test_split(
        X_all, y_all, test_size=0.2, stratify=y_all, random_state=RANDOM_STATE
    )
    X_test, y_test = test[features], test["target"]

    final_model = build_pipeline(
        RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1),
        CATEGORICAL,
    )
    final_model.fit(X_train, y_train)

    # Headline numbers for the banner (official test set, final model)
    pred = final_model.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    b = Bundle()
    b.model = final_model
    b.features = features
    b.numeric = numeric
    b.categorical = CATEGORICAL
    b.X_val, b.y_val = X_val, y_val
    b.metrics = {
        "Accuracy": accuracy_score(y_test, pred),
        "Recall": recall_score(y_test, pred, zero_division=0),
        "False positive rate": fp / (fp + tn),
    }
    defaults = {c: float(X_train[c].median()) for c in numeric}
    defaults.update({c: X_train[c].mode()[0] for c in CATEGORICAL})
    b.defaults = defaults
    b.protocols = sorted(X_train["protocol_type"].unique().tolist())
    b.services = sorted(X_train["service"].unique().tolist())
    b.flags = sorted(X_train["flag"].unique().tolist())
    return b


# ── Prediction ───────────────────────────────────────────────────────────────
def alert_level(prob):
    """Turn an attack probability into a simple alert level."""
    if prob >= 0.90:
        return "High"
    if prob >= 0.50:
        return "Medium"
    return "Low"


def predict_connections(b, df):
    """Check the input, then predict normal/attack for every row."""
    if df is None or len(df) == 0:
        raise ValueError("The file is empty.")

    missing_cols = [c for c in b.features if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    X = df[b.features].copy()
    for col in b.numeric:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    if X[b.numeric].isna().any().any():
        raise ValueError("Some number columns contain text or empty values.")
    if (X[b.numeric] < 0).any().any():
        raise ValueError("Negative values were found. Please check the data.")

    prob = b.model.predict_proba(X)[:, 1]
    return pd.DataFrame({
        "row": np.arange(1, len(X) + 1),
        "protocol_type": X["protocol_type"].values,
        "service": X["service"].values,
        "flag": X["flag"].values,
        "prediction": np.where(prob >= ATTACK_THRESHOLD, "Attack", "Normal"),
        "attack_probability": prob.round(4),
        "alert_level": [alert_level(p) for p in prob],
    })


# ── HTML building blocks (styled by APP_CSS) ─────────────────────────────────
def esc(x):
    return _html.escape(str(x))


def empty_card(message):
    return f'<div class="nids-empty">{esc(message)}</div>'


def error_card(message):
    return (f'<div class="nids-card nids-attack"><div class="nids-verdict">Something went wrong</div>'
            f'<p class="nids-note">{esc(message)}</p></div>')


def result_card(prediction, prob, level, extra=""):
    tone = "attack" if prediction == "Attack" else "normal"
    title = "Attack detected" if prediction == "Attack" else "Looks normal"
    return f"""
    <div class="nids-card nids-{tone}">
      <div class="nids-verdict"><span class="nids-dot"></span>{title}</div>
      <div class="nids-prob">{prob * 100:.1f}<small>%</small></div>
      <div class="nids-sub">attack probability</div>
      <div class="nids-meter"><div class="nids-fill" style="width:{prob * 100:.1f}%"></div>
        <div class="nids-tick" style="left:{ATTACK_THRESHOLD * 100:.0f}%"></div></div>
      <div class="nids-scale"><span>0%</span><span>threshold {ATTACK_THRESHOLD:.0%}</span><span>100%</span></div>
      <div class="nids-chips"><span class="nids-chip nids-lvl-{level.lower()}">{level} alert</span></div>
      {extra}
    </div>"""


def stat_tiles(items):
    """items = [(label, value, tone)]"""
    return '<div class="nids-tiles">' + "".join(
        f'<div class="nids-tile nids-t-{t}"><span>{esc(l)}</span><b>{esc(v)}</b></div>' for l, v, t in items
    ) + "</div>"


# ── Functions the screen calls ───────────────────────────────────────────────
def check_one(b, protocol, service, flag, src_bytes, dst_bytes, conn_count, serror_rate, logged_in):
    """Predict for one connection. Fields not shown in the form use typical values."""
    row = dict(b.defaults)
    row.update({
        "protocol_type": protocol, "service": service, "flag": flag,
        "src_bytes": src_bytes or 0, "dst_bytes": dst_bytes or 0,
        "count": conn_count or 0, "logged_in": int(logged_in),
    })
    # A SYN flood raises all four SYN-error features together, so one slider sets them all
    for col in ["serror_rate", "srv_serror_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate"]:
        row[col] = serror_rate
    try:
        res = predict_connections(b, pd.DataFrame([row])).iloc[0]
    except Exception as e:
        return error_card(e)
    return result_card(res["prediction"], res["attack_probability"], res["alert_level"])


def read_uploaded_file(file):
    """Read an uploaded file (bytes or a Streamlit upload), with or without a header row."""
    data = file.getvalue() if hasattr(file, "getvalue") else bytes(file)
    first_line = data.split(b"\n", 1)[0].decode("utf-8", errors="ignore")
    if "duration" in first_line.lower():
        return pd.read_csv(io.BytesIO(data), sep=None, engine="python")
    df = pd.read_csv(io.BytesIO(data), sep=None, engine="python", header=None)
    n = df.shape[1]
    if n < 41 or n > len(COLUMNS):
        raise ValueError(f"Expected 41 to {len(COLUMNS)} columns, found {n}.")
    df.columns = COLUMNS[:n]
    return df


def check_file(b, file):
    """Predict for every row of an uploaded file. Returns (summary_html, table)."""
    if file is None:
        return empty_card("Upload a file to see the results."), pd.DataFrame()
    try:
        res = predict_connections(b, read_uploaded_file(file))
    except Exception as e:
        return error_card(e), pd.DataFrame()
    n = len(res)
    n_attack = int((res["prediction"] == "Attack").sum())
    levels = res["alert_level"].value_counts()
    summary = stat_tiles([
        ("Records checked", f"{n:,}", "neutral"),
        (f"Flagged as attack ({n_attack / n:.1%})", f"{n_attack:,}", "bad" if n_attack else "good"),
        ("High alerts", f"{int(levels.get('High', 0)):,}", "bad"),
        ("Medium", f"{int(levels.get('Medium', 0)):,}", "warn"),
        ("Low", f"{int(levels.get('Low', 0)):,}", "good"),
    ]) + '<p class="nids-note">The table shows the 500 highest-risk rows.</p>'
    return summary, res.sort_values("attack_probability", ascending=False).head(500)


def random_example(b):
    """Pick a real validation record and compare the model with the true label."""
    i = int(np.random.randint(len(b.X_val)))
    row = b.X_val.iloc[[i]]
    truth = "Attack" if b.y_val.iloc[i] == 1 else "Normal"
    res = predict_connections(b, row).iloc[0]
    correct = res["prediction"] == truth
    r = row.iloc[0]
    details = f"""
      <div class="nids-compare">
        <div><span>Real label</span><b>{truth}</b></div>
        <div><span>Model says</span><b>{res['prediction']}</b></div>
        <div class="nids-{'ok' if correct else 'bad'}"><span>Result</span><b>{'✓ Correct' if correct else '✗ Wrong'}</b></div>
      </div>
      <table class="nids-kv">
        <tr><td>Protocol</td><td>{esc(r['protocol_type'])}</td><td>Service</td><td>{esc(r['service'])}</td></tr>
        <tr><td>Flag</td><td>{esc(r['flag'])}</td><td>Count</td><td>{esc(r['count'])}</td></tr>
        <tr><td>Bytes sent</td><td>{esc(r['src_bytes'])}</td><td>Bytes received</td><td>{esc(r['dst_bytes'])}</td></tr>
      </table>"""
    return result_card(res["prediction"], res["attack_probability"], res["alert_level"], details)


def model_snapshot(b):
    """Headline numbers for the banner (official test set, final model)."""
    m = b.metrics
    return stat_tiles([("Test accuracy", f"{m['Accuracy']:.1%}", "neutral"),
                       ("Attack recall", f"{m['Recall']:.1%}", "warn"),
                       ("False alarms", f"{m['False positive rate']:.1%}", "good"),
                       ("Features", str(len(b.features)), "neutral")])
