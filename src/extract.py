import requests

def extreure_dades_aire() -> list:
    """
    Fa una crida a l'API de Socrata de la Generalitat de Catalunya
    per obtenir les dades de qualitat de l'aire (XVPCA).
    """
    url_endpoint = "https://analisi.transparenciacatalunya.cat/resource/tasf-thgu.json"
    
    # Configurem els paràmetres de l'API de Socrata (SODA)
    parametres = {
        "municipi": municipi, # type: ignore
        "$limit": limit # type: ignore
    }
    
    try:
        # Fem la petició HTTP GET
        resposta = requests.get(url_endpoint)
        
        # Això llançarà una excepció si el codi de resposta és un error (4xx o 5xx)
        resposta.raise_for_status()
        
        # Si tot ha anat bé, retornem el JSON transformat en una llista de Python
        return resposta.json()
        
    except requests.exceptions.RequestException as error:
        print(f"Error crític durant l'extracció de dades: {error}")
        return []

if __name__ == "__main__":
    print("Iniciant el procés d'extracció de proves...")
    
    # Fem una crida de prova per defecte (Barcelona, 50 registres)
    dades_en_brut = extreure_dades_aire()
    
    if dades_en_brut:
        print(f"¡Èxit! S'han extret {len(dades_en_brut)} registres correctament.")
        print("\nExemple de l'estructura del primer registre rebut:")
        print(dades_en_brut[0])
    else:
        print("No s'ha pogut recuperar cap dada. Revisa la connexió o l'endpoint.")