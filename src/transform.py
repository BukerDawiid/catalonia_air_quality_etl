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

    columnes_identificadores = [
        'codi_provincia', 'provincia', 'codi_municipi', 'municipi', 
        'nom_estacio', 'codi_eoi', 'data', 'magnitud', 'contaminant', 'unitats',
        'punt_mostreig'
    ]
    
    columnes_hores = [f'h{i:02d}' for i in range(1, 25)]
    columnes_hores_presents = [col for col in columnes_hores if col in df_cru.columns]

    df_llarg = pd.melt(
        df_cru, 
        id_vars=[col for col in columnes_identificadores if col in df_cru.columns], 
        value_vars=columnes_hores_presents, 
        var_name='hora', 
        value_name='valor_mesura'
    )
    
    df_llarg['hora'] = df_llarg['hora'].str.replace('h', '').astype(int)
    df_llarg['valor_mesura'] = pd.to_numeric(df_llarg['valor_mesura'], errors='coerce')

    df_llarg['data'] = pd.to_datetime(df_llarg['data'])
    
    columnes_desitjades = ['data', 'nom_estacio', 'hora']
    columnes_ordenacio = [col for col in columnes_desitjades if col in df_llarg.columns]
    
    df_net = df_llarg.dropna(subset=['valor_mesura']).sort_values(by=columnes_ordenacio)
    
    return df_net

if __name__ == "__main__":
    print("Iniciant el procés d'extracció i transformació...")
    
    # Cridem la funció sense paràmetres, ja que ara és massiva i intel·ligent
    dades_json = extreure_dades_aire()
    
    df_resultat = transformar_dades_aire(dades_json)
    
    print(f"\nS'han generat {len(df_resultat)} registres horaris nets.")
    print("\nMostra del DataFrame final llest per pujar a la base de dades:")
    
    columnes_pantalla = ['nom_estacio', 'municipi', 'contaminant', 'data', 'hora', 'valor_mesura']
    columnes_a_imprimir = [col for col in columnes_pantalla if col in df_resultat.columns]
    
    print(df_resultat[columnes_a_imprimir].head(10))