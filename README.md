# Catalonia Air Quality ETL Pipeline

An automated Data Engineering pipeline designed to extract, transform, and load (ETL) air quality metrics from the Generalitat de Catalunya Open Data portal into a cloud-hosted PostgreSQL database.

## 🏗️ Architecture & Tech Stack

- **Extraction:** Retrieves raw JSON data from the Socrata API (`requests`).
- **Transformation:** Normalizes horizontal hourly data into a vertical, tidy data format (`pandas`).
- **Load:** Injects the processed data into a cloud database (`sqlalchemy`, `psycopg2`).
- **Storage:** PostgreSQL database hosted on Supabase.
- **Orchestration:** Fully automated via GitHub Actions with a daily cron job.

## ⚙️ How it Works

1. **Extract:** Queries the Socrata API endpoint for the *Xarxa d'Estacions de Prevenció i Vigilància de la Contaminació Atmosfèrica i Acústica* (XVPCA).
2. **Transform:** Melts the 24-hour horizontal column structure (`h01` to `h24`) into a normalized, time-series vertical format. Ensures proper data typing and handles API missing values defensively.
3. **Load:** Connects to a Supabase PostgreSQL instance via a secure Session Pooler (IPv4 compatible) and appends the new daily records.

## 🚀 Local Setup

To run this pipeline locally, you will need Python 3.9+ and a Supabase account.

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/catalonia_air_quality_etl.git](https://github.com/your-username/catalonia_air_quality_etl.git)
   cd catalonia_air_quality_etl

2. Create and activate a virtual environment:

    ```Bash
    python -m venv venv
    source venv/bin/activate

3. Install dependencies:

    ```Bash
    pip install -r requirements.txt

4. Create a .env file in the root directory and add your Supabase connection string:

    DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@aws-0-[REGION][.pooler.supabase.com:5432/postgres](https://.pooler.supabase.com:5432/postgres)
    (Note: Ensure special characters in your password are URL-encoded).

5. Run the pipeline:

    ```Bash
    python -m src.load
    
👤 Author
David Rescalvo Rius | Computer Engineer & Data Solutions