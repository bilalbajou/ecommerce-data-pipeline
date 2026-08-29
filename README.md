# 🛒 E-Commerce Data Pipeline

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Wrangling-150458?logo=pandas&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Tested-0A9EDC?logo=pytest&logoColor=white)

A production-grade, containerized **ETL (Extract, Transform, Load)** pipeline built in Python. This project ingests raw product catalog data from an external REST API, performs extensive data cleansing and schema normalization, and securely incrementally upserts the analytics-ready data into a PostgreSQL database.

## ✨ Features

- **Intelligent Extraction**: Safely paginates through REST APIs using dynamic limit/skip logic to fetch the complete dataset without timeouts.
- **Robust Transformation**: Cleans nested JSON structures, standardizes column names to `snake_case`, handles missing values, and dynamically calculates business metrics (e.g., `final_price`).
- **True Incremental Loading**: Utilizes advanced PostgreSQL `INSERT ... ON CONFLICT DO UPDATE ... WHERE` combined with `RETURNING xmax` to execute true database-level incremental upserts (identifying precisely which rows were inserted, updated, or unchanged).
- **Data Quality Validation**: Strictly validates the loaded data against business constraints (e.g., zero nulls in required fields, positive stock, price formula consistency).
- **Fully Dockerized**: Completely reproducible environment using Docker and Docker Compose.
- **Comprehensive Testing**: Covered by a robust `pytest` suite simulating end-to-end load logic into a temporary database.

## 🏗️ Architecture

1. **`Extract`** (`src/extract.py`): Paginates `https://dummyjson.com/products` and dumps raw JSON.
2. **`Transform`** (`src/transform.py`): Converts raw JSON to a cleansed, flattened Pandas DataFrame.
3. **`Load`** (`src/load.py`): Incrementally upserts data into the PostgreSQL `products` table.
4. **`Validate`** (`src/validate.py`): Asserts data quality integrity against the database.
5. **`Pipeline`** (`src/pipeline.py`): The central orchestrator that manages dependencies, tracks execution metrics, and gracefully handles fatal errors.

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose (Recommended)
- *OR* Python 3.11+ and a local PostgreSQL instance

### 1. Configuration
Copy the `.env.example` file to create your local `.env`:
```bash
cp .env.example .env
```
Ensure your database credentials in `.env` are set (e.g., `POSTGRES_USER=postgres`).

### 2. Run via Docker (Recommended)
The easiest way to run the pipeline is to let Docker handle the PostgreSQL setup and Python environment.

```bash
# Spin up the Database and run the ETL pipeline
docker compose up --build
```
*Note: The ETL container will automatically wait for the Postgres container to be healthy before executing.*

### 3. Run Locally (Without Docker)
If you prefer running it on your host machine:

```powershell
# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the pipeline orchestrator
python -m src.pipeline
```

---

## 🧪 Testing
The project features an automated test suite verifying transformation logic and database upserts.
```bash
# Ensure your virtual environment is active
pytest tests/
```

## 📊 Analytics
Once the data is loaded, you can generate business insights (like total inventory value, average ratings by category, and low stock alerts). 
Check out the ready-to-use analytical queries in:
[`sql/analytics.sql`](sql/analytics.sql)

## 📁 Project Structure
```text
ecommerce-data-pipeline/
├── data/                  # Local storage for raw JSON and processed CSV
├── sql/                   # Analytical SQL queries
│   └── analytics.sql
├── src/                   # Core ETL pipeline source code
│   ├── config.py          # Centralized environment configuration
│   ├── logger.py          # Structured logging
│   ├── extract.py         # API Extraction logic
│   ├── transform.py       # Pandas Transformation logic
│   ├── load.py            # PostgreSQL Incremental Load logic
│   ├── validate.py        # Data Quality checks
│   └── pipeline.py        # Main ETL Orchestrator
├── tests/                 # Pytest test suite
├── .env                   # Local Environment variables
├── .dockerignore          # Docker build exclusions
├── .gitignore             # Git tracking exclusions
├── docker-compose.yml     # Multi-container orchestration
├── Dockerfile             # Python application image definition
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```
