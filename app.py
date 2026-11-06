"""Streamlit view of the synthetic data-asset catalog."""

from pathlib import Path

import streamlit as st

from inventory import AS_OF, DB_PATH, build_database, load_frame, metrics

st.set_page_config(page_title="Data asset inventory", layout="wide")
st.title("Data asset inventory")
st.caption(
    "Synthetic catalog only. Sensitivity, owners, stewards, and agreement dates are invented for practice."
)

if not Path(DB_PATH).exists():
    build_database()

summary = metrics()
left, middle, right = st.columns(3)
left.metric("Classified", f"{summary['percent_classified']}%")
middle.metric("Agreements expired", f"{summary['percent_agreements_expired']}%")
right.metric("No owner", f"{summary['percent_without_owner']}%")
st.caption(f"Measured against {summary['assets']} assets as of {AS_OF.isoformat()}.")

frame = load_frame()
sensitivity = st.multiselect(
    "Sensitivity",
    ["Public", "Internal", "Confidential", "Restricted-PHI", "(unclassified)"],
    default=["Public", "Internal", "Confidential", "Restricted-PHI", "(unclassified)"],
)
shown = frame.copy()
shown["sensitivity"] = shown["sensitivity"].fillna("(unclassified)")
shown = shown[shown["sensitivity"].isin(sensitivity)]
expired_only = st.checkbox("Expired agreements only")
if expired_only:
    shown = shown[shown["agreement_expiry"].notna() & (shown["agreement_expiry"] < AS_OF)]
st.dataframe(shown, use_container_width=True, hide_index=True)
