import pandas as pd
from src.extract import extreure_dades_aire

def transformar_dades_aire(dades_en_brut: list) -> pd.DataFrame:
    """
    Transforma el JSON de l'API de format horitzontal (24 columnes d'hores)
    a format vertical (tidy data) utilitzant Pandas.
    """
    df_cru = pd.DataFrame(dades_en_brut)
    
    if df_cru.empty:
        print("No hi ha dades per transformar.")
        return pd.DataFrame()

    # 1. Definim les columnes fixes utilitzant el nom correcte de la documentació
    columnes_identificadores = [
        'codi_provincia', 'provincia', 'codi_municipi', 'municipi', 
        'nom_estacio', 'codi_eoi', 'data', 'magnitud', 'contaminant', 'unitats',
        'punt_mostreig'
    ]
    
    columnes_hores = [f'h{i:02d}' for i in range(1, 25)]
    columnes_hores_presents = [col for col in columnes_hores if col in df_cru.columns]

    # 2. Passem de format ample a format llarg
    df_llarg = pd.melt(
        df_cru, 
        id_vars=[col for col in columnes_identificadores if col in df_cru.columns], 
        value_vars=columnes_hores_presents, 
        var_name='hora', 
        value_name='valor_mesura'
    )
    
    # 3. Neteja i tipatge
    df_llarg['hora'] = df_llarg['hora'].str.replace('h', '').astype(int)
    df_llarg['valor_mesura'] = pd.to_numeric(df_llarg['valor_mesura'], errors='coerce')

    df_llarg['data'] = pd.to_datetime(df_llarg['data'])
    
    # 4. Ordenació defensiva utilitzant la clau correcta
    columnes_desitjades = ['data', 'nom_estacio', 'hora']
    columnes_ordenacio = [col for col in columnes_desitjades if col in df_llarg.columns]
    
    df_net = df_llarg.dropna(subset=['valor_mesura']).sort_values(by=columnes_ordenacio)
    
    return df_net

if __name__ == "__main__":
    print("Iniciant el procés d'extracció i transformació...")
    
    # Extraiem una mostra de dades
    dades_json = extreure_dades_aire(limit=5)
    
    # Executem la transformació corregida
    df_resultat = transformar_dades_aire(dades_json)
    
    print(f"\nS'han generat {len(df_resultat)} registres horaris nets.")
    print("\nMostra del DataFrame final llest per pujar a la base de dades:")
    
    # Mostrem el resultat filtrant de forma segura per pantalla
    columnes_pantalla = ['nom_estacio', 'municipi', 'contaminant', 'data', 'hora', 'valor_mesura']
    columnes_a_imprimir = [col for col in columnes_pantalla if col in df_resultat.columns]
    
    print(df_resultat[columnes_a_imprimir].head(10))