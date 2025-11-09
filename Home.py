# Home.py
from pathlib import Path
import json
import pandas as pd
import streamlit as st

# Local imports
from utils.paths import schema_png, DATA_DIR

# --- Streamlit page setup ---
st.set_page_config(
    page_title="Climate-Adaptive Variety + Irrigation + Smart Nutrients recommender",
    layout="wide"
)

# --- Title ---
st.title("🌿 Climate-Adaptive Variety + Irrigation + Smart Nutrients Recommender")

# --- Hero: show ONLY the schema image ---
schema = schema_png()
if schema.exists():
    st.image(str(schema), caption="Knowledge Graph — Metagraph (schema overview)", use_container_width=True)
else:
    st.info("Schema PNG not found in the data directory (schema_metagraph.png).")

# --- Project summary (short) ---
st.markdown("## What this project is about")
st.markdown(
    """
This mini-app presents a **knowledge-graph–driven agronomy recommender** that blends:

- **Variety selection**, **irrigation needs**, and **nutrient (N-P-K) planning**  
- **Climate windows** and stage-wise crop dynamics  
- Optional **disease risk** signals

The underlying knowledge graph captures entities like regions, crops, climate windows, stages, and plans, then links them with typed relationships (e.g., *REGION_HAS_CLIMATE*, *CLIMATE_SUPPORTS_STAGE*, *PLAN_USES_VARIETY*). We pair this graph structure with **RAG-style retrieval** to surface relevant connections and evidence, which in turn power the **recommendation tables as shown below**. The result is a transparent trail from recommendations back to the climate/stage/variety context that supports them.
"""
)

# --- Pages overview (renamed) ---
st.markdown("## Pages at a glance")
st.markdown(
    """
- **Page 1 — The Blueprint**: Simple, visual orientation using ready-made example figures.  
- **Page 2 — Season Snapshots**: Per-region, per-crop *season subgraphs* (2024) to show how climate windows connect to crop stages.  
- **Page 3 — Climate Snapshots**: Country/region/year gallery of *climate-centric subgraphs* to compare climate→stage link density across space and time.
"""
)

# =============================================================================
# New: Interact with recommendation tables (NaN-safe, lightweight)
# =============================================================================
st.markdown("## Explore the recommendation tables")

# Where the parquet/json live (WSL path via utils.paths.DATA_DIR)
REC_DIR: Path = DATA_DIR

FILES = {
    "default": REC_DIR / "recommendations.parquet",
    "balanced": REC_DIR / "recommendations_balanced.parquet",
    "low_water": REC_DIR / "recommendations_low_water.parquet",
    "low_n": REC_DIR / "recommendations_low_n.parquet",
    "disease_aware": REC_DIR / "recommendations_disease_aware.parquet",
    "robust": REC_DIR / "recommendations_robust.parquet",
}
META_PATH = REC_DIR / "recommendations_meta.json"

existing_presets = [k for k, p in FILES.items() if p.exists()]

@st.cache_data(show_spinner=False)
def load_one(kind: str) -> pd.DataFrame:
    """Load one parquet and tag its source. Returns empty DF if not found."""
    p = FILES.get(kind)
    if not p or not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df["__source__"] = kind
    return df

@st.cache_data(show_spinner=False)
def load_all(kinds: list[str]) -> pd.DataFrame:
    dfs = [load_one(k) for k in kinds]
    dfs = [d for d in dfs if not d.empty]
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True, sort=False)

@st.cache_data(show_spinner=False)
def load_meta() -> dict:
    if META_PATH.exists():
        try:
            return json.loads(META_PATH.read_text())
        except Exception:
            return {}
    return {}

if not existing_presets:
    st.warning(f"No recommendation parquet files found in: {REC_DIR}")
else:
    # --- Controls
    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 1])
    with c1:
        sel_preset = st.selectbox("Preset (table source)", existing_presets, index=0)
    df = load_one(sel_preset)

    # Derive choices safely
    crops = sorted(df["crop"].dropna().unique().tolist()) if "crop" in df else []
    regions = sorted(df["region_iso"].dropna().unique().tolist()) if "region_iso" in df else []
    years = sorted(df["year"].dropna().unique().tolist()) if "year" in df else []

    with c2:
        sel_crop = st.selectbox("Crop", crops, index=0 if crops else None)
    with c3:
        sel_region = st.selectbox("Region", regions, index=0 if regions else None)
    with c4:
        min_score = st.slider("Min plan_score", 0.0, 1.0, 0.0, 0.01)

    # Optional: multi-year filter if present
    sel_years = st.multiselect("Years (optional)", years, default=years)

    # Hide-NaNs toggle: drops rows with NaNs in the key columns that exist
    st.markdown("**Display options**")
    hide_nans = st.checkbox("Only show rows without NaNs in key columns", value=True)

    # Build a row mask
    mask = pd.Series(True, index=df.index)
    if "crop" in df and sel_crop:
        mask &= df["crop"].eq(sel_crop)
    if "region_iso" in df and sel_region:
        mask &= df["region_iso"].eq(sel_region)
    if "year" in df and sel_years:
        mask &= df["year"].isin(sel_years)
    if "plan_score" in df:
        mask &= df["plan_score"].fillna(0) >= float(min_score)

    # Columns to show (only those that exist)
    preferred_cols = [
        "region_iso", "crop", "variety", "year",
        "plan_score", "variety_fit", "disease_fit",
        "irr_total_mm", "etc_total_mm", "pe_total_mm", "rainfall_share",
        "n_kg_ha", "p_kg_ha", "k_kg_ha", "net_irrig_mm_sel",
        "robust_score", "rank_plan", "__source__"
    ]
    show_cols = [c for c in preferred_cols if c in df.columns]

    view = df.loc[mask, show_cols]

    # If requested, drop rows with NaNs in "key" columns that actually exist here
    key_cols = [c for c in ["plan_score", "disease_fit", "variety_fit"] if c in view.columns]
    if hide_nans and key_cols:
        view = view.dropna(subset=key_cols)

    # Sort by score if it exists
    if "plan_score" in view.columns:
        view = view.sort_values("plan_score", ascending=False)

    # Show a compact table (trim to first 500 rows for responsiveness)
    st.dataframe(view.head(500), use_container_width=True)

    with st.expander("About these tables (source files & schema)", expanded=False):
        st.write("Directory:", str(REC_DIR))
        st.write("Loaded file:", str(FILES[sel_preset]))
        st.caption(
            "Tip: switch presets to see how the same (region, crop) looks under different objectives, "
            "and toggle **Only show rows without NaNs** to hide sparse columns."
        )
        meta = load_meta()
        if meta:
            st.json(meta)

# --- Navigation reminder ---
st.info("Use the left sidebar to navigate between **The Blueprint**, **Season Snapshots**, and **Climate Snapshots**.")