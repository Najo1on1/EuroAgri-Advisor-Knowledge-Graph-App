# 1_The_Blueprint.py
from pathlib import Path
import streamlit as st

# If you created utils/paths.py earlier, prefer importing the base dir:
#   from utils.paths import CROP_APP_DATA
# and set BASE = CROP_APP_DATA
# For this page we'll point directly to the WSL path you provided.
BASE = Path("/mnt/d/Colab/Ecosystem/Deep RL and LLM/Agri/data/processed/kg/crop_app_data")

st.title("The Blueprint")

st.markdown(
    """
    Below are **quick visual examples** for each crop.  
    For every crop we show:
    - **Overview**: the high-level crop subgraph
    - **Region Matrix**: per-region top plans (mini-panels)
    - **Climate Matrix**: simplified Plan → Region → ClimateWindow  view
    """
)

# Extra description of the plots shown below
st.markdown(
    """
The `subgraph_crop_{crop}.png` panel is the core knowledge-graph view, it shows how plans are grounded in place. Each plan node points into a region node via `PLAN_APPLIES_TO` and carries links to variety, nutrient caps, and stage logic. Our retrieval engine walks this topology to assemble an evidence pack using climate windows, disease risk, irrigation need followed by computation of `plan_score` and confidence. The `_matrix.png` aggregates these results into readable per-region panels (top-k). The `_climate_matrix.png` focuses on seasonal context, visualizing how monthly climate windows support specific stages, which explains irrigation and disease terms attached to each plan.
    """
)

# Crop order + file patterns (under crop_app_data/)
CROPS = [
    "maize", "wheat", "sugarbeet", "rapeseed",
    "potato", "peas", "beans", "barley"
]

def trio_paths(crop: str):
    """Return (overview, region_matrix, climate_matrix) PNG paths for a crop."""
    crop = crop.lower().strip()
    p_overview = BASE / f"subgraph_crop_{crop}.png"
    p_matrix   = BASE / f"subgraph_crop_{crop}_matrix.png"
    p_climate  = BASE / f"subgraph_crop_{crop}_climate_matrix.png"
    return p_overview, p_matrix, p_climate

# Render each crop in an expander with a 3-column gallery
for crop in CROPS:
    p_overview, p_matrix, p_climate = trio_paths(crop)

    with st.expander(f"{crop.capitalize()} — Quick Examples", expanded=False):
        cols = st.columns(3, gap="large")

        # Overview
        if p_overview.exists():
            cols[0].image(str(p_overview), caption=p_overview.name, use_container_width=True)
        else:
            cols[0].warning(f"Missing: {p_overview}")

        # Region Matrix
        if p_matrix.exists():
            cols[1].image(str(p_matrix), caption=p_matrix.name, use_container_width=True)
        else:
            cols[1].warning(f"Missing: {p_matrix}")

        # Climate Matrix
        if p_climate.exists():
            cols[2].image(str(p_climate), caption=p_climate.name, use_container_width=True)
        else:
            cols[2].warning(f"Missing: {p_climate}")

st.markdown("---")
st.info("Images are read from the WSL path: "
        f"`{BASE}`")