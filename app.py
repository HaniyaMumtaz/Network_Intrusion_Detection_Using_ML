from pathlib import Path

import pandas as pd
import streamlit as st

import nids_core as nc

DATA_DIR = Path(__file__).parent / "data"
TRAIN_PATH = DATA_DIR / "KDDTrain+.txt"
TEST_PATH = DATA_DIR / "KDDTest+.txt"

st.set_page_config(page_title="Network Intrusion Detection System", page_icon="🛡️", layout="wide")

# Same look as the notebook's APP_CSS, written with neutral colours so it works in light and dark mode.
APP_CSS = """
<style>
.block-container { max-width: 1120px; }
.nids-hero { background: linear-gradient(120deg,#4f46e5 0%,#7c3aed 55%,#db2777 100%); color:#fff;
             border-radius:18px; padding:26px 30px; margin-bottom:6px; }
.nids-hero h1 { margin:0; padding:0; font-size:28px; font-weight:750; letter-spacing:-.02em; color:#fff; }
.nids-hero p { margin:6px 0 0; opacity:.9; font-size:14.5px; max-width:720px; line-height:1.5; color:#fff; }
.nids-badges { margin-top:14px; display:flex; gap:8px; flex-wrap:wrap; }
.nids-badges span { background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.28);
                    padding:3px 11px; border-radius:99px; font-size:12px; color:#fff; }
.nids-tiles { display:flex; gap:10px; flex-wrap:wrap; margin:6px 0; }
.nids-tile { flex:1; min-width:120px; padding:11px 14px; border-radius:12px; border:1px solid rgba(128,128,128,.3);
             background:rgba(128,128,128,.07); box-shadow:inset 0 3px 0 #6366f1; }
.nids-tile span { display:block; font-size:11px; text-transform:uppercase; letter-spacing:.06em; opacity:.65; }
.nids-tile b { font-size:19px; white-space:nowrap; }
.nids-t-good { box-shadow:inset 0 3px 0 #14b8a6; } .nids-t-bad { box-shadow:inset 0 3px 0 #f43f5e; } .nids-t-warn { box-shadow:inset 0 3px 0 #f59e0b; }
.nids-card { border-radius:16px; padding:22px 24px; border:1px solid rgba(128,128,128,.3);
             background:rgba(128,128,128,.07); border-left:6px solid #14b8a6; }
.nids-card.nids-attack { border-left-color:#f43f5e; }
.nids-verdict { font-weight:700; font-size:14px; text-transform:uppercase; letter-spacing:.08em; color:#0d9488; display:flex; align-items:center; gap:8px; }
.nids-attack .nids-verdict { color:#e11d48; }
.nids-dot { width:10px; height:10px; border-radius:50%; background:#14b8a6; box-shadow:0 0 0 4px rgba(20,184,166,.25); }
.nids-attack .nids-dot { background:#f43f5e; box-shadow:0 0 0 4px rgba(244,63,94,.25); }
.nids-prob { font-size:60px; font-weight:800; line-height:1.05; margin-top:10px; letter-spacing:-.03em; }
.nids-prob small { font-size:26px; opacity:.6; margin-left:2px; }
.nids-sub { opacity:.65; font-size:13px; margin-bottom:14px; }
.nids-meter { position:relative; height:12px; border-radius:99px; background:rgba(128,128,128,.3); overflow:visible; }
.nids-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#14b8a6,#f59e0b 55%,#f43f5e); }
.nids-tick { position:absolute; top:-4px; width:2px; height:20px; background:currentColor; opacity:.55; }
.nids-scale { display:flex; justify-content:space-between; font-size:11px; opacity:.55; margin-top:6px; }
.nids-chips { margin-top:14px; }
.nids-chip { display:inline-block; padding:4px 12px; border-radius:99px; font-size:12.5px; font-weight:600; }
.nids-lvl-low { background:#ccfbf1; color:#0f766e; } .nids-lvl-medium { background:#fef3c7; color:#b45309; }
.nids-lvl-high { background:#ffe4e6; color:#be123c; }
.nids-empty { border:2px dashed rgba(128,128,128,.4); border-radius:16px; padding:46px 20px; text-align:center; opacity:.65; }
.nids-note { opacity:.65; font-size:13px; margin:8px 2px 0; }
.nids-compare { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:18px; }
.nids-compare div { padding:10px 12px; border-radius:10px; background:rgba(128,128,128,.08); border:1px solid rgba(128,128,128,.3); }
.nids-compare span { display:block; font-size:11px; text-transform:uppercase; letter-spacing:.06em; opacity:.6; }
.nids-compare b { font-size:16px; } .nids-ok b { color:#0d9488; } .nids-bad b { color:#e11d48; }
.nids-kv { width:100%; margin-top:14px; border-collapse:collapse; font-size:13.5px; }
.nids-kv td { padding:6px 8px; border:none; border-bottom:1px solid rgba(128,128,128,.3); }
.nids-kv td:nth-child(odd) { opacity:.6; width:18%; }
.nids-footer { text-align:center; opacity:.55; font-size:12px; margin-top:10px; }
</style>
"""

HERO = """
<div class="nids-hero">
  <h1>🛡️ Network Intrusion Detection</h1>
  <p>A classroom prototype that flags suspicious network connections using a Random Forest trained on
     NSL-KDD. It supports human review and must not be used for real security decisions.</p>
  <div class="nids-badges"><span>Random Forest</span><span>NSL-KDD</span><span>Prototype</span></div>
</div>"""


def show_html(markup):
    """Show HTML. Indentation and blank lines are removed first, because Markdown would turn them into code blocks."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()), unsafe_allow_html=True)


# ── Train the model once (cached for every visitor) ──────────────────────────
@st.cache_resource(show_spinner="Training the Random Forest on NSL-KDD. This happens once, about a minute ...")
def get_bundle():
    return nc.train_bundle(TRAIN_PATH, TEST_PATH)


show_html(APP_CSS)

missing = [p.name for p in (TRAIN_PATH, TEST_PATH) if not p.exists()]
if missing:
    st.error(f"Missing data file(s): {', '.join(missing)}. Upload them into the 'data' folder of the GitHub repo.")
    st.stop()

b = get_bundle()

show_html(HERO)
show_html(nc.model_snapshot(b))

# ── Widget defaults (set once, so the preset buttons can change them) ────────
for key, value in {"one_protocol": "tcp", "one_service": "http", "one_flag": "SF",
                   "one_src": 200.0, "one_dst": 1000.0, "one_count": 5.0,
                   "one_serror": 0.0, "one_logged": True}.items():
    st.session_state.setdefault(key, value)


def apply_preset(name):
    p, s, f, src, dst, cnt, ser, li = nc.PRESETS[name]
    st.session_state.update(one_protocol=p, one_service=s, one_flag=f, one_src=float(src),
                            one_dst=float(dst), one_count=float(cnt), one_serror=float(ser),
                            one_logged=bool(li), pending_check=True)


def request_check():
    st.session_state["pending_check"] = True


tab_one, tab_file, tab_rand = st.tabs(["Check one connection", "Check a file", "Random real example"])

# ── Tab 1: one connection ────────────────────────────────────────────────────
with tab_one:
    st.markdown("Start with a preset, or tweak the fields yourself. Anything not shown here uses a typical value.")
    c1, c2, c3, _ = st.columns([1, 1, 1.2, 2])
    c1.button("🌐 Normal web browsing", on_click=apply_preset, args=("normal",))
    c2.button("🌊 SYN flood", on_click=apply_preset, args=("syn",))
    c3.button("📡 ICMP (smurf) flood", on_click=apply_preset, args=("smurf",))

    left, right = st.columns([5, 4], gap="large")
    with left:
        a, bb, c = st.columns(3)
        protocol = a.selectbox("Protocol", b.protocols, key="one_protocol")
        service = bb.selectbox("Service", b.services, key="one_service")
        flag = c.selectbox("Flag (connection status)", b.flags, key="one_flag")
        d, e = st.columns(2)
        src_bytes = d.number_input("Bytes sent (src_bytes)", step=1.0, format="%g", key="one_src")
        dst_bytes = e.number_input("Bytes received (dst_bytes)", step=1.0, format="%g", key="one_dst")
        conn_count = st.number_input("Connections to the same host in the last 2 seconds (count)",
                                     step=1.0, format="%g", key="one_count")
        serror_rate = st.slider("SYN error rate (sets all 4 SYN-error features)",
                                0.0, 1.0, step=0.05, key="one_serror")
        logged_in = st.checkbox("Logged in", key="one_logged")
        st.button("Check connection", type="primary", on_click=request_check)

    if st.session_state.pop("pending_check", False):
        st.session_state["one_result"] = nc.check_one(
            b, protocol, service, flag, src_bytes, dst_bytes, conn_count, serror_rate, logged_in)
    with right:
        show_html(st.session_state.get("one_result",
                  nc.empty_card("Pick a preset or press “Check connection”.")))

# ── Tab 2: a file ────────────────────────────────────────────────────────────
with tab_file:
    st.markdown("Upload a `.txt` or `.csv` file of connection records "
                "(same columns as KDDTrain+.txt, with or without a header row).")
    f_left, f_right = st.columns([3, 5], gap="large")
    with f_left:
        uploaded = st.file_uploader("Connection records file", type=["txt", "csv"])
        if st.button("Check file", type="primary"):
            st.session_state["file_result"] = nc.check_file(b, uploaded)
    summary, table = st.session_state.get(
        "file_result", (nc.empty_card("Upload a file to see the results."), pd.DataFrame()))
    with f_right:
        show_html(summary)
    st.caption("Results (highest risk first)")
    st.dataframe(table, hide_index=True)

# ── Tab 3: random real example ───────────────────────────────────────────────
with tab_rand:
    st.markdown("Picks a real connection from the validation data and compares the model with the true label.")
    if st.button("🎲 Show a random example", type="primary"):
        st.session_state["rand_result"] = nc.random_example(b)
    show_html(st.session_state.get("rand_result", nc.empty_card("Press the button to draw a record.")))

show_html('<div class="nids-footer">Educational prototype · trained on NSL-KDD · not for production security decisions</div>')
