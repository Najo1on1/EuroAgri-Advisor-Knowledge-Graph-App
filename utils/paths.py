# utils/paths.py
from pathlib import Path

# Point directly to your WSL path (no copying required)
DATA_DIR = Path("/mnt/d/Colab/Ecosystem/Deep RL and LLM/Agri/data/processed/kg/crop_app_data")

KG_APP_DIR = DATA_DIR

def crops_available():
    """
    Discover crops by looking for the matrix images you already export:
    subgraph_crop_{crop}_matrix.png
    """
    if not DATA_DIR.exists():
        return []
    items = []
    for p in DATA_DIR.glob("subgraph_crop_*_matrix.png"):
        # e.g., subgraph_crop_wheat_matrix.png -> wheat
        name = p.stem.replace("subgraph_crop_", "").replace("_matrix", "")
        if name:
            items.append(name)
    return sorted(set(items))

def png(pathname: str) -> Path:
    """Convenience to return a Path inside DATA_DIR."""
    return DATA_DIR / pathname

def crop_pngs(crop: str):
    """
    Return all known PNG variants for a given crop.
    Some files might not exist; callers should check .exists().
    """
    crop = str(crop).lower().strip()
    return {
        "initial_overview": png(f"subgraph_crop_{crop}.png"),
        "initial_matrix":   png(f"subgraph_crop_{crop}_matrix.png"),
        "climate":          png(f"subgraph_crop_{crop}_climate.png"),
        "climate_matrix":   png(f"subgraph_crop_{crop}_climate_matrix.png"),
        "disease":          png(f"subgraph_crop_{crop}_disease.png"),
        "disease_matrix":   png(f"subgraph_crop_{crop}_disease_matrix.png"),
        "graphml":          png(f"graph_crop_{crop}.graphml"),  # not displayed on pages 2–3
    }

def schema_png():
    """Return the schema metagraph image Path."""
    return png("schema_metagraph.png")

def season_examples():
    """Return a sorted list of any available seasonal subgraph images."""
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.glob("subgraph_season_*_*.png"))