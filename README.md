# Smart City Mobility Analytics — Antananarivo, Madagascar

An interactive urban mobility analytics platform built with Python, Elasticsearch, and Streamlit. The project simulates urban trips across 17 neighborhoods of Antananarivo, Madagascar, and provides interactive dashboards to explore mobility patterns.

> **Data note:** The 10,000 trips are synthetically generated for academic and analytical purposes. They are not real traffic measurements or official mobility records.

## Project Overview

The application explores simulated mobility patterns by:
- Hour of day
- Departure and arrival neighborhoods
- Vehicle type
- Weather conditions
- Congestion level
- Trip distance, duration, and average speed

## Architecture

1. **Data Generation — Python**  
   `data/generate_data.py` generates 10,000 synthetic trip documents and exports a CSV copy (`mobility_tana.csv`).

2. **Indexing — Elasticsearch**  
   `elastic/index.py` creates the `smart_city_mobility` index and defines field mappings, including geographic point fields.

3. **Ingestion — Elasticsearch Bulk API**  
   The generated documents are inserted into Elasticsearch by `data/generate_data.py`.

4. **Queries and Aggregations — Python + Elasticsearch**  
   `agregations/queries.py` executes filtered searches and aggregations.

5. **Interactive Interface — Streamlit**  
   `app/main.py` provides the home page, while the pages in `app/pages/` provide the dashboard and data exploration interface. Pandas prepares query results and Plotly renders charts.

## Main Features

- Traffic volume by hour.
- Most frequently used departure and arrival neighborhoods.
- Comparison of trip duration by weather condition.
- Vehicle statistics: trip counts, average distance, duration, and speed.
- Interactive filters by vehicle, weather, and time range.

## Technology Stack

- Python
- Elasticsearch 8.18
- Streamlit
- Pandas
- Plotly
- Docker Compose

## Project Structure

```text
smart-city-mobility-analytics/
├── agregations/
│   └── queries.py
├── app/
│   ├── main.py
│   └── pages/
│       ├── dashboard.py
│       └── exploration.py
├── data/
│   └── generate_data.py
├── elastic/
│   └── index.py
├── mobility_tana.csv
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Run Locally

### 1. Prerequisites

- Python 3.10 or newer
- Docker Desktop with Docker Compose
- Git (optional, for cloning the repository)

### 2. Clone the repository

```bash
git clone https://github.com/malala1105/smart-city-mobility-analytics.git
cd smart-city-mobility-analytics
```

### 3. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start Elasticsearch

```bash
docker compose up -d
```

Wait until Elasticsearch is ready at `http://localhost:9200`.

### 6. Create the Elasticsearch index

```bash
python elastic/index.py
```

> **Warning:** The index script deletes an existing `smart_city_mobility` index before recreating it. Running it again removes the currently indexed documents.

### 7. Generate and index the synthetic trips

```bash
python data/generate_data.py
```

This generates and indexes 10,000 trips and exports `mobility_tana.csv` in the current working directory.

### 8. Launch the Streamlit application

```bash
streamlit run app/main.py
```

Streamlit will display a local URL in the terminal (usually `http://localhost:8501`).

## Notes and Limitations

- The dataset is synthetic; patterns reflect the assumptions encoded in the generation script.
- Distances are estimated from neighborhood coordinates using a simplified road-distance factor, not measured GPS routes.
- Weather, congestion, vehicle distributions, and trip purposes are simulated.
- The application requires a running local Elasticsearch instance populated with the generated index.

## Author

**Iangotiana Noro Malala Andrianoelisoa**

---

*Developed as an academic portfolio project focused on urban mobility analytics in Antananarivo, Madagascar.*
