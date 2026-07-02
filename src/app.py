import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.express as px

# Carreguem les variables d'entorn en local
load_dotenv()

# Configuració de la pàgina de Streamlit
st.set_page_config(
    page_title="Catalonia Air Quality Dashboard",
    page_icon="🍃",
    layout="wide"
)

# Funció per connectar a la base de dades i descarregar les dades
@st.cache_data(ttl=600)  # Guarda les dades en memòria 10 minuts perquè la web vagi súper ràpida
def obtenir_dades_db():
    # Streamlit al cloud llegeix de st.secrets, en local d'os.getenv
    url_connexio = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")
    
    if not url_connexio:
        st.error("Error: No s'ha trobat la configuració de la base de dades.")
        return pd.DataFrame()
        
    try:
        motor_db = create_engine(url_connexio)
        # Fem una consulta SQL per portar-nos les dades guardades per l'ETL
        consulta = "SELECT * FROM mesures_qualitat_aire;"
        df = pd.read_sql(consulta, con=motor_db)
        return df
    except Exception as e:
        st.error(f"Error en connectar a la base de dades: {e}")
        return pd.DataFrame()

# --- INTERFÍCIE VISUAL ---
st.title("🍃 Control de Qualitat de l'Aire a Catalunya")
st.markdown("Aquest dashboard interactiu consumeix les dades extretes de l'API de la Generalitat de Catalunya i emmagatzemades al cloud de Supabase.")

# Descarreguem les dades
df_mesures = obtenir_dades_db()

if df_mesures.empty:
    st.warning("No hi ha dades disponibles en aquest moment.")
else:
    # 1. Filtres a la barra lateral (Sidebar)
    st.sidebar.header("Filtres de Cerca")
    
    # Filtre de municipi/estació de forma defensiva
    columna_lloc = 'municipi' if 'municipi' in df_mesures.columns else 'nom_estacio'
    llista_llocs = sorted(df_mesures[columna_lloc].unique())
    lloc_seleccionat = st.sidebar.selectbox("Selecciona una Estació/Municipi:", llista_llocs)
    
    # Filtre de contaminant
    llista_contaminants = sorted(df_mesures['contaminant'].unique())
    contaminant_seleccionat = st.sidebar.selectbox("Selecciona el Contaminant:", llista_contaminants)

    # 2. Filtratge del DataFrame segons la interacció de l'usuari
    df_filtrat = df_mesures[
        (df_mesures[columna_lloc] == lloc_seleccionat) & 
        (df_mesures['contaminant'] == contaminant_seleccionat)
    ]

    # 3. Mètriques Clau (KPIs)
    st.subheader(f"Estat actual a: {lloc_seleccionat}")
    
    if not df_filtrat.empty:
        # Agafem la darrera mesura registrada
        ultima_fila = df_filtrat.iloc[-1]
        unitats = ultima_fila.get('unitats', 'µg/m³')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"Última lectura de {contaminant_seleccionat}", value=f"{ultima_fila['valor_mesura']} {unitats}")
        with col2:
            st.metric(label="Mitjana diària registrada", value=f"{round(df_filtrat['valor_mesura'].mean(), 2)} {unitats}")
        with col3:
            st.metric(label="Lectura Màxima", value=f"{df_filtrat['valor_mesura'].max()} {unitats}")

        # 4. Gràfic d'Evolució Temporal
        st.subheader("📊 Evolució horària dels nivells de contaminació")
        
        df_grafic = df_filtrat.copy()
        df_grafic = df_grafic.sort_values(by='hora')
        
        # Preparem les dades per al gràfic de línies de Streamlit
        df_chart_data = df_grafic.set_index('hora')[['valor_mesura']]
        df_chart_data.columns = [f"Nivell de {contaminant_seleccionat}"]
        
        # Pintem el gràfic interactiu nativament
        st.line_chart(df_chart_data)
        
        # 5. Taula de dades crues filtrades
        st.subheader("📋 Històric de dades estructurades")
        st.dataframe(df_filtrat, use_container_width=True)
    else:
        st.info("No s'han trobat registres que coincideixin amb els filtres seleccionats.")

# --- MAPA INTERACTIU ---
    st.subheader(f"🗺️ Mapa en temps real: {contaminant_seleccionat}")
    
    # Filtrem totes les dades per quedar-nos només amb el contaminant que estem mirant
    df_mapa = df_mesures[df_mesures['contaminant'] == contaminant_seleccionat].copy()
    
    if not df_mapa.empty and 'latitud' in df_mapa.columns:
        # Ens quedem només amb l'última mesura disponible de cada estació
        df_mapa = df_mapa.sort_values('hora').drop_duplicates('nom_estacio', keep='last')
        
        # Assegurem que les coordenades són números (a vegades l'API les envia com a text)
        df_mapa['latitud'] = pd.to_numeric(df_mapa['latitud'], errors='coerce')
        df_mapa['longitud'] = pd.to_numeric(df_mapa['longitud'], errors='coerce')
        df_mapa = df_mapa.dropna(subset=['latitud', 'longitud', 'valor_mesura'])
        
        # Creem el mapa amb Plotly
        figura_mapa = px.scatter_mapbox(
            df_mapa,
            lat="latitud",
            lon="longitud",
            color="valor_mesura",  # El color dependrà del nivell de contaminació
            size="valor_mesura",   # La mida de la bombolla també
            hover_name="nom_estacio", # Text que surt al posar el ratolí
            hover_data={"valor_mesura": True, "latitud": False, "longitud": False},
            color_continuous_scale=px.colors.sequential.YlOrRd, # Escala de Groc a Vermell
            zoom=6.5,
            center={"lat": 41.8, "lon": 1.5}, # Centrat aproximadament a Catalunya
            mapbox_style="carto-positron",    # Estil de mapa clar per destacar els colors
        )
        
        # Ajustem els marges perquè ocupi bé l'espai
        figura_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        # Ho enviem a la pantalla de Streamlit
        st.plotly_chart(figura_mapa, use_container_width=True)
    else:
        st.info("No hi ha dades geogràfiques disponibles per a aquest contaminant.")