import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from src.extract import extreure_dades_aire
from src.transform import transformar_dades_aire

# Carreguem les variables ocultes del fitxer .env
load_dotenv()

def carregar_dades_base_dades(df: pd.DataFrame, nom_taula: str = "mesures_qualitat_aire") -> bool:
    """
    Connecta amb la base de dades PostgreSQL remota de Supabase i injecta 
    el DataFrame de Pandas directament en una taula de SQL.
    """
    if df.empty:
        print("El DataFrame està buit. Cancel·lant la fase de càrrega.")
        return False

    # Recuperem la URI de connexió segura del fitxer .env
    url_connexio = os.getenv("DATABASE_URL")
    if not url_connexio:
        print("Error: La variable d'entorn DATABASE_URL no està configurada al fitxer .env")
        return False

    try:
        # Creem el motor de connexió de SQLAlchemy
        motor_db = create_engine(url_connexio)
        
        print(f"Connectant al cloud de Supabase i enviant {len(df)} registres...")
        
        # Injectem les dades. 
        # Si la taula no existeix, Pandas la crearà de zero automàticament.
        # Si ja existeix, hi afegirà les noves files (append).
        df.to_sql(nom_taula, con=motor_db, if_exists='append', index=False)
        
        print(f"¡Èxit! Dades carregades correctament a la taula '{nom_taula}'.")
        return True
        
    except Exception as error:
        print(f"Error crític durant la càrrega a la base de dades: {error}")
        return False

if __name__ == "__main__":
    print("Executant l'ETL completa en mode de prova...")
    
    # 1. Extracció (Demanem 20 registres de mostra per provar)
    dades_en_brut = extreure_dades_aire(limit=20)
    
    # 2. Transformació (Passem a format vertical amb Pandas)
    df_net = transformar_dades_aire(dades_en_brut)
    
    # 3. Càrrega (Enviem el resultat final a PostgreSQL)
    carregar_dades_base_dades(df_net)