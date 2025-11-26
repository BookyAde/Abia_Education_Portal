import os
import sqlalchemy
from sqlalchemy import create_engine, text

# Define the 17 LGAs of Abia State
ABIA_LGAS = [
    "Aba North", "Aba South", "Arochukwu", "Bende", "Ikwuano", 
    "Isiala Ngwa North", "Isiala Ngwa South", "Isuikwuato", "Obi Ngwa", 
    "Ohafia", "Osisioma", "Ugwunagbo", "Ukwa East", "Ukwa West", 
    "Umuahia North", "Umuahia South", "Umu Nneochi"
]

def get_database_url():
    # Check for environment variables or secrets
    # This allows it to run locally if env vars are set, or you can manually replace this string
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    
    if not all([db_user, db_password, db_host, db_name]):
        print("❌ Error: Missing database credentials.")
        print("Please ensure DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME are set in your environment or secrets.")
        return None
        
    return f"postgresql+pg8000://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def setup_database():
    url = get_database_url()
    if not url:
        return

    print(f"🔌 Connecting to database...")
    try:
        engine = create_engine(url)
        with engine.begin() as conn:
            # 1. Create Schema
            print("Creating schema 'dwh'...")
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS dwh;"))

            # 2. Create Dimensions Table (LGA)
            print("Creating table 'dwh.dim_lga'...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dwh.dim_lga (
                    lga_key SERIAL PRIMARY KEY,
                    lga_name VARCHAR(100) UNIQUE NOT NULL
                );
            """))

            # 3. Create Submissions Table
            print("Creating table 'school_submissions'...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS school_submissions (
                    id SERIAL PRIMARY KEY,
                    school_name VARCHAR(255) NOT NULL,
                    lga_name VARCHAR(100) NOT NULL,
                    enrollment_total INTEGER DEFAULT 0,
                    teachers_total INTEGER DEFAULT 0,
                    submitted_by VARCHAR(100),
                    email VARCHAR(100),
                    submitted_at TIMESTAMP DEFAULT NOW(),
                    approved BOOLEAN DEFAULT NULL
                );
            """))

            # 4. Create Fact Table
            print("Creating table 'dwh.fact_abia_metrics'...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS dwh.fact_abia_metrics (
                    lga_key INTEGER PRIMARY KEY REFERENCES dwh.dim_lga(lga_key),
                    enrollment_total INTEGER DEFAULT 0,
                    teachers_total INTEGER DEFAULT 0,
                    approved BOOLEAN DEFAULT TRUE
                );
            """))

            # 5. Populate LGAs
            print("Populating LGAs...")
            for lga in ABIA_LGAS:
                conn.execute(text("""
                    INSERT INTO dwh.dim_lga (lga_name) 
                    VALUES (:lga) 
                    ON CONFLICT (lga_name) DO NOTHING;
                """), {"lga": lga})
            
            print("✅ Database setup complete! All tables created and LGAs populated.")

    except Exception as e:
        print(f"❌ Error during setup: {e}")

if __name__ == "__main__":
    setup_database()
