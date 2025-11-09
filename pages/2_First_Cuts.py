# pages/2_First_Cuts.py
from pathlib import Path
import streamlit as st

# Use the shared paths module from utils/
from utils.paths import KG_APP_DIR

st.set_page_config(page_title="Season Snapshots", layout="wide")

st.title("🗺️ Season Snapshots")

# Intro description (focus on subgraph_season_{region}_{year}_{crop}.png)
st.markdown(
    """
The **subgraph_season** plots reveal the fine-grained mechanics behind our agronomy recommender.  
Each network maps how a region’s **climate windows** (blue) feed into **growth stages** (grey) via
relationships such as **REGION_HAS_CLIMATE** and **CLIMATE_SUPPORTS_STAGE**. Orange nodes mark
seasonally high **disease risk** derived from humidity–temperature interactions. This temporal
graph is built from our **Climate Windows** pipeline (ERA5 → ET₀/ETc, water-balance weeks) and
encoded in the **Knowledge Graph**, enabling **RAG-style** reasoning that connects real weather
patterns to irrigation need, disease fit, and variety performance across 2024.
"""
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SEASON_CROPS = [
    "barley", "beans", "maize", "peas", "potato", "rapeseed", "sugarbeet", "wheat"
]

def season_png(region: str, crop: str) -> Path:
    """
    Build the WSL path to season images living under:
    /mnt/d/Colab/Ecosystem/Deep RL and LLM/Agri/data/processed/kg/crop_app_data
    Example filename: subgraph_season_BE-BE22_2024_wheat.png
    """
    return KG_APP_DIR / f"subgraph_season_{region}_2024_{crop}.png"

def show_region_grid(region: str, crops=SEASON_CROPS, cols_per_row: int = 4):
    st.subheader(f"Region: {region}")
    rows = [crops[i:i+cols_per_row] for i in range(0, len(crops), cols_per_row)]
    for row in rows:
        cols = st.columns(len(row))
        for c, col in zip(row, cols):
            p = season_png(region, c)
            if p.exists():
                col.image(str(p), caption=p.name, use_container_width=True)
            else:
                col.warning(f"Missing: {p.name}")

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

# Region BE-BE10
show_region_grid("BE-BE10")

# Region BE-BE21
show_region_grid("BE-BE21")

# Region BE-BE22
show_region_grid("BE-BE22")

with st.expander("What you're seeing in the subgraph_season_{region}_{year}_{crop name}.png examples?"):
    st.markdown(
        """
These *Season Subgraphs* are time-aware graphs that tie regional weather to crop development and risk.
Large blue nodes are **ClimateWindow** aggregates (derived from ERA5), summarising multi-week patterns
in temperature, rainfall, radiation and derived ET₀/ETc. Grey nodes are **StageWindow** entries for the
phenology sequence (emergence → vegetative → reproductive → maturity). Fine-grained **WaterBalanceWeek**
nodes (teal) sit underneath, capturing weekly moisture balance used to infer irrigation demand. When the
climate variables and leaf-wetness proxies indicate heightened pathogen favourability, we annotate
**DiseaseStageRisk** (orange) at the relevant stages.

Edges encode the semantics that the **Knowledge Graph** uses for retrieval:

**REGION_HAS_CLIMATE** links the place to its seasonal climate, while **CLIMATE_SUPPORTS_STAGE**
(and related edges) show when climate is suitable for each stage. During recommendation, our RAG engine
walks these edges to build an *evidence pack* for a (region, year, crop): stage timing, water-balance
pressure, and disease risk corridors. That evidence informs component fits i.e. **irrigation need**,
**disease fit**, and (when available) **variety fit**, which combine into the final **plan_score** and
**confidence**. In short, each picture is a provenance map that explains *why* a plan scores the way it
does by grounding the recommendation in seasonal dynamics that are both spatially (region) and temporally
(2024 windows and weeks) explicit.
        """
    )
