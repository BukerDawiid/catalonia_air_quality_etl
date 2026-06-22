import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

def carregar_dades_db(df: pd.DataFrame):
    if df.empty:
        print("No hi ha dades noves per pujar a Supabase.")
        return

    load_dotenv()
    url_connexio = os.getenv("DATABASE_URL")
    
    if not url_connexio:
        print("Error: DATABASE_URL no configurada.")
        return

    try:
        motor_db = create_engine(url_connexio)
        
        # L'script busca la data mínima que acaba d'arribar de l'extracció
        data_tall_dinamica = df['data'].min()
        data_tall_str = data_tall_dinamica.strftime('%Y-%m-%d') if hasattr(data_tall_dinamica, 'strftime') else str(data_tall_dinamica)[:10]

        # INSTANCIEM L'INSPECTOR per comprovar si la taula ja existeix
        inspector = inspect(motor_db)
        
        if 'mesures_qualitat_aire' in inspector.get_table_names():
            # Si existeix, fem la neteja anti-duplicats
            with motor_db.connect() as connexio:
                print(f"Netejant la base de dades a partir del {data_tall_str} per integrar els nous registres...")
                consulta_esborrat = text(f"DELETE FROM mesures_qualitat_aire WHERE data >= '{data_tall_str}'")
                connexio.execute(consulta_esborrat)
                connexio.commit()
        else:
            # Si no existeix, ens saltem el DELETE
            print("La taula no existeix a Supabase. Es crearà automàticament de zero ara.")
            
        # Inserim les dades
        print("Inserint les dades...")
        df.to_sql('mesures_qualitat_aire', con=motor_db, if_exists='append', index=False)
        print(f"Càrrega completada! S'han sincronitzat {len(df)} files a Supabase.")
        
    except Exception as error:
        print(f"Error crític durant la càrrega: {error}")

if __name__ == "__main__":
    pass