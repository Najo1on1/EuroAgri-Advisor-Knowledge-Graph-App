# pages/3_Sharper_Views.py
from pathlib import Path
import streamlit as st
from utils.paths import KG_APP_DIR

st.set_page_config(page_title="Sharper Views — Climate Snapshots", layout="wide")

# ---------------------------------------------------------------------
# Title & short intro
# ---------------------------------------------------------------------
st.title("🔎 Climate Snapshots")

st.markdown(
    """
    These climate snapshots visualize how our **Climate Windows** pipeline is materialized in the **Knowledge Graph**.  
    Each figure anchors a single `ClimateWindow` node for a given region–year, then fans out to the `StageWindow` nodes it supports through `CLIMATE_SUPPORTS_STAGE` edges.  
    Months are encoded by hue; stages by categorical color, so you can see when **emergence**, **vegetative**, **reproductive**, and **maturity** are most climate-supported.  
    Under the hood, we generate these windows from **ERA5-Land** features, **ET₀/ETc** derivatives, and **water-balance** logic, then store them as typed nodes and relations.  
    This enables graph traversal and **RAG** retrieval that tie seasonal context directly to agronomy plans.
    """
)

with st.expander("How to read these figures (quick)"):
    st.markdown(
        """
Each image shows a **ClimateWindow** node linked to many **StageWindow** nodes.
- **Solid edge** from the **Region** node to the **ClimateWindow**.
- **Dotted edges** from **ClimateWindow** to **StageWindow** nodes (downstream crop-stage support).
- Node colors hint month (Jan/Apr/Jul/Oct) and stage category (emergence → maturity).

Use this gallery to quickly compare seasonal climate–stage link density across regions/years.
        """
    )

# ---------------------------------------------------------------------
# Discover available climate images
# Pattern: subgraph_climate_{REGION}_{YEAR}_1.png
# Example: subgraph_climate_BE-BE21_2019_1.png
# ---------------------------------------------------------------------
def list_climate_images():
    files = sorted(KG_APP_DIR.glob("subgraph_climate_*_*_1.png"))
    items = []
    for p in files:
        # name like: subgraph_climate_BE-BE21_2019_1.png
        stem = p.stem  # "subgraph_climate_BE-BE21_2019_1"
        parts = stem.split("_")
        if len(parts) < 5:
            continue
        region = parts[2]          # e.g., "BE-BE21"
        year = parts[3]            # e.g., "2019"
        country = region.split("-")[0] if "-" in region else "??"
        items.append({"path": p, "country": country, "region": region, "year": year})
    return items

ALL = list_climate_images()
if not ALL:
    st.warning("No climate images found in: {}".format(KG_APP_DIR))
    st.stop()

# ---------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    countries = sorted({x["country"] for x in ALL})
    sel_countries = st.multiselect("Country", countries, default=countries)

    filtered = [x for x in ALL if x["country"] in sel_countries] if sel_countries else ALL

    regions = sorted({x["region"] for x in filtered})
    # If there are many, preselect none to encourage scoping
    sel_regions = st.multiselect("Region", regions, default=[])

    if sel_regions:
        filtered = [x for x in filtered if x["region"] in sel_regions]

    years = sorted({x["year"] for x in filtered})
    sel_years = st.multiselect("Year", years, default=years[:1] if years else [])

    if sel_years:
        filtered = [x for x in filtered if x["year"] in sel_years]

    st.markdown("---")
    ncols = st.slider("Columns per row", min_value=2, max_value=4, value=3)
    page_size = st.slider("Images per page", min_value=6, max_value=24, value=12, step=3)

# Nothing after filtering?
if not filtered:
    st.info("No images match the current filters.")
    st.stop()

# ---------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------
total = len(filtered)
pages = (total + page_size - 1) // page_size
page_idx = st.number_input("Page", min_value=1, max_value=max(1, pages), value=1, step=1)
start = (page_idx - 1) * page_size
end = start + page_size
page_items = filtered[start:end]

st.write(f"Showing **{len(page_items)}** of **{total}** images  •  Page {page_idx}/{pages}")

# ---------------------------------------------------------------------
# Grid renderer
# ---------------------------------------------------------------------
def show_grid(items, ncols: int):
    rows = [items[i:i+ncols] for i in range(0, len(items), ncols)]
    for row in rows:
        cols = st.columns(len(row))
        for cell, col in zip(row, cols):
            cap = f"{cell['path'].name}  \n{cell['region']} • {cell['year']}"
            col.image(str(cell["path"]), caption=cap, use_container_width=True)

# Group by Country to avoid visual overload
for c in sorted({x["country"] for x in page_items}):
    sub = [x for x in page_items if x["country"] == c]
    if not sub:
        continue
    with st.expander(f"Country: {c}  — {len(sub)} image(s)", expanded=True if len(page_items) <= 12 else False):
        show_grid(sub, ncols=ncols)

st.markdown("---")
st.caption(f"Source: {KG_APP_DIR}")

with st.expander("What you're seeing in the subgraph_climate_{region}_{year}_1.png examples?"):
    st.markdown(
        """
Each **subgraph_climate** figure is the transformation from raw climate to actionable stage timing, expressed as a graph.  
For a given **{region, year}**, we compute climate derivatives (**ET₀** via Penman–Monteith, **ETc** by crop, **effective rainfall**, **VPD**, **humidity** patterns) and roll them into a **ClimateWindow** node.  
The single **solid edge** binds that window to its **Region**.  
The **dotted edges** then enumerate which **StageWindow** nodes are climatically supported—this is a direct encoding of our suitability logic (thresholds/scores on moisture, temperature, radiation, and balance).  
**Month hue** and **stage color** make the season readable: you can spot whether **emergence** is front-loaded, how long **vegetative** conditions persist, and whether **reproductive/maturity** phases bunch into drier or hotter months.  
Because this structure is stored in a **typed Knowledge Graph**, the recommender can retrieve exactly the windows that matter for a crop in that place and year.  
Those retrieved pieces are combined with **disease-risk** and **irrigation** tracks to produce transparent plan explanations.  
Thus, the subgraph communicates both the **data lineage** (ERA5 → engineered features → windows) and the **reasoning path** the system uses to justify plan choices.
        """
    )