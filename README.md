# 🌍 EuroAgri Advisor — Knowledge Graph App

This repository hosts the **interactive visualization layer** of the EuroAgri-Advisor ecosystem, a Streamlit-based app that turns complex agronomic datasets into an interpretable **Knowledge Graph interface**.  
The assumption is that it connects directly to the structured outputs of the [EuroAgri-Pipeline](https://github.com/Najo1on1/euroagri-pipeline).

---

## 🧠 What This App Does

The app renders visual layers of the EuroAgri Knowledge Graph:

- **🏗️ The Blueprint** – shows crop-level subgraphs linking regions, plans, and climate windows.  
- **🗺️ Season Snapshots** – reveals per-region seasonal subgraphs (climate → stages → crops).  
- **🔎 Climate Snapshots** – focuses on how monthly climate windows support different crop stages.

Each view reads `.png` and `.parquet` exports from the EuroAgri Pipeline, offering a lightweight front-end to navigate thousands of graph relationships built from soil, climate, disease, and yield datasets.

---

## ⚙️ Quick Start

```bash
# Clone and install
git clone https://github.com/Najo1on1/EuroAgri-Advisor-Knowledge-Graph-App.git
cd EuroAgri-Advisor-Knowledge-Graph-App
pip install -r requirements.txt

# Launch the app
streamlit run Home.py
````

Make sure your data folder structure mirrors:

```
data/processed/kg/crop_app_data/
├── subgraph_crop_wheat.png
├── subgraph_season_BE-BE22_2024_wheat.png
└── subgraph_climate_BE-BE22_2020_1.png
```

---

## 🧩 Connection to EuroAgri Pipeline

This app visualizes the artifacts produced by the **EuroAgri-Pipeline**, particularly:

* `/data/processed/kg/crop_app_data` (graph snapshots, matrices)
* `/data/processed/recommendations.parquet` (underlying recommendation data)
* `/docs/` (metadata and methods)

By connecting to these outputs, the app forms the visual interface for exploring the reasoning layers of EuroAgri Advisor - from soils and climate to crop recommendations.

---

## 🪪 License

MIT License
© 2025 Muwanguzi Jonathan
