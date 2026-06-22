from src.extract import extreure_dades_aire
from src.transform import transformar_dades_aire
from src.load import carregar_dades_db

def executar_pipeline():
    print("🚀 Iniciant la pipeline de dades...")
    
    # 1. EXTRACCIÓ
    dades_crues = extreure_dades_aire()
    if not dades_crues:
        print("🛑 Procés aturat: No hi ha dades noves per descarregar o hi ha hagut un error.")
        return

    # 2. TRANSFORMACIÓ
    print("⚙️ Transformant les dades al format correcte...")
    df_net = transformar_dades_aire(dades_crues)
    if df_net.empty:
        print("🛑 Procés aturat: El DataFrame resultant està buit.")
        return

    # 3. CÀRREGA
    carregar_dades_db(df_net)
    
    print("✅ Pipeline completada amb èxit!")

if __name__ == "__main__":
    executar_pipeline()