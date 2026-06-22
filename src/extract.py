import os
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def obtenir_ultima_data_db() -> str:
    """Consulta Supabase per saber quina és la dada més recent que tenim."""
    load_dotenv()
    url_connexio = os.getenv("DATABASE_URL")
    
    if not url_connexio:
        return None

    try:
        motor_db = create_engine(url_connexio)
        with motor_db.connect() as connexio:
            resultat = connexio.execute(text("SELECT MAX(data) FROM mesures_qualitat_aire"))
            max_data = resultat.scalar()
            
            if max_data:
                return max_data[:10] if isinstance(max_data, str) else max_data.strftime('%Y-%m-%d')
            return None
    except Exception as e:
        print("Avís: La base de dades està buida o la taula no existeix encara.")
        return None

def extreure_dades_aire() -> list:
    """Extracció intel·ligent (High-Water Mark) resistent a errors."""
    
    # 1. Obtenim la data més recent de l'API de Socrata
    url_max = "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json?$select=max(data)"
    try:
        resposta_max = requests.get(url_max)
        resposta_max.raise_for_status()
        ultima_data_api = resposta_max.json()[0].get('max_data')
        
        if not ultima_data_api:
            print("Error: L'API no ha retornat cap data.")
            return []
        
        ultima_data_api = ultima_data_api[:10]
    except Exception as e:
        print(f"Error crític connectant a l'API: {e}")
        return []

    # 2. Obtenim la nostra última data
    ultima_data_db = obtenir_ultima_data_db()
    
    # 3. Presa de decisions
    if not ultima_data_db:
        print("No hi ha historial a Supabase. Executant càrrega inicial (darrers 7 dies)...")
        data_tall = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    elif ultima_data_api > ultima_data_db:
        print(f"Novetats detectades! L'API arriba fins al {ultima_data_api}. Nosaltres estem al {ultima_data_db}.")
        data_tall = ultima_data_db
    else:
        print(f"El sistema està 100% sincronitzat (Última dada: {ultima_data_db}). Cancel·lant extracció innecessària.")
        return []

    # 4. Descarreguem exactament el delta necessari
    url_endpoint = "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json"
    parametres = {
        "$where": f"data >= '{data_tall}'",
        "$limit": 50000 
    }
    
    try:
        print(f"Descarregant el paquet de dades des del {data_tall}...")
        resposta = requests.get(url_endpoint, params=parametres)
        resposta.raise_for_status()
        dades = resposta.json()
        print(f"Extracció completada: {len(dades)} registres nous llestos per transformar.")
        return dades
    except Exception as e:
        print(f"Error durant la descàrrega de novetats: {e}")
        return []

if __name__ == "__main__":
    dades_noves = extreure_dades_aire()