# Installation des dépendances nécessaires :
# pip install kagglehub pandas numpy streamlit
import pandas as pd
import numpy as np
import streamlit as st

# Configuration de la page Streamlit
st.set_page_config(page_title="Classement des Buteurs", layout="wide")
st.title("🏆 Classement des buteurs les plus probables")

try:
    import kagglehub
    from kagglehub import KaggleDatasetAdapter
except ImportError:
    st.error("Le module kagglehub n'est pas installé. Installez-le avec : pip install kagglehub[pandas-datasets]")
    kagglehub = None

# Chargement des données avec cache pour éviter les rechargements inutiles
@st.cache_data
def load_data():
    file_path = "players_data-2025_2026.csv"
    
    if kagglehub:
        try:
            df = kagglehub.load_dataset(
                KaggleDatasetAdapter.PANDAS,
                "hubertsidorowicz/football-players-stats-2025-2026",
                file_path,
            )
        except Exception as e:
            st.error(f"Erreur lors du chargement depuis Kaggle: {e}")
            df = pd.DataFrame()
    else:
        # Fallback : lecture locale si kagglehub non disponible
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            st.error(f"Impossible de charger le fichier CSV : {e}")
            df = pd.DataFrame()
    
    # Conversion explicite en DataFrame pandas si besoin
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    
    return df

# Chargement des données
df = load_data()

# Vérification que les données sont chargées
if df.empty:
    st.error("Aucune donnée n'a pu être chargée. Vérifiez la source des données.")
    st.stop()

# Vérification des colonnes nécessaires
colonnes_obligatoires = ['Player', 'Gls', 'MP', 'Sh', 'xG']
colonnes_manquantes = [col for col in colonnes_obligatoires if col not in df.columns]

if colonnes_manquantes:
    st.error(f"Colonnes manquantes : {', '.join(colonnes_manquantes)}")
    st.stop()

# Sidebar pour les contrôles
st.sidebar.header("Paramètres d'affichage")
nombre_joueurs = st.sidebar.slider("Nombre de joueurs à afficher", 5, 50, 10)

# Calcul des ratios pour évaluer la probabilité de marquer
df['ratio_buts_par_match'] = df['Gls'] / df['MP']
df['ratio_buts_par_tir'] = df['Gls'] / df['Sh']
df['tirs_par_match'] = df['Sh'] / df['MP']
df['xG_par_match'] = df['xG'] / df['MP']

# Nettoyage des valeurs infinies (inf) et remplacement par NaN
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Remplacer les NaN par 0 pour les calculs
df.fillna(0, inplace=True)

# Calcul des probabilités de marquer pour chaque joueur
df['Score_perf_offensive'] = (
    df['xG_par_match'] * 0.4 + 
    df['ratio_buts_par_tir'] * 0.25 + 
    df['ratio_buts_par_match'] * 0.2 + 
    df['tirs_par_match'] * 0.15
)

# Classement avancé des buteurs
classement_avance = df.sort_values(
    by=['Score_perf_offensive', 'xG_par_match', 'xG', 'ratio_buts_par_tir', 'ratio_buts_par_match', 'tirs_par_match', 'Gls'], 
    ascending=False
)

# Formatage des colonnes numériques
columns_to_format = ['Score_perf_offensive', 'xG_par_match', 'ratio_buts_par_tir', 'ratio_buts_par_match', 'tirs_par_match']

# Créer une copie pour l'affichage avec les valeurs formatées
df_display = classement_avance.copy()

for col in columns_to_format:
    if col == 'probabilite_buteur_%':
        df_display[col] = df_display[col].round(2)
    else:
        df_display[col] = df_display[col].round(3)

# Affichage du tableau
st.subheader(f"Top {nombre_joueurs} des buteurs les plus probables")

# Sélection des colonnes à afficher
colonnes_a_afficher = ['Player', 'Gls','MP', 'xG_par_match', 'Score_perf_offensive','xG','ratio_buts_par_tir', 'ratio_buts_par_match', 'tirs_par_match']

# Vérifier que les colonnes existent
colonnes_disponibles = [col for col in colonnes_a_afficher if col in df_display.columns]

if len(colonnes_disponibles) != len(colonnes_a_afficher):
    st.warning("Certaines colonnes ne sont pas disponibles dans le dataset")

# Afficher le dataframe
st.dataframe(
    df_display[colonnes_disponibles].head(nombre_joueurs),
    use_container_width=True,
    height=400
)

# Bouton de rafraîchissement
if st.button('🔄 Rafraîchir les données'):
    st.cache_data.clear()
    st.experimental_rerun()

# Informations supplémentaires
st.sidebar.markdown("---")
st.sidebar.subheader("À propos")
st.sidebar.info("""
Cette analyse combine plusieurs métriques :
- **xG par match** : Expected Goals par match
- **Ratio buts/tir** : Efficacité des tirs
- **Ratio buts/match** : Fréquence de buts
- **Tirs par match** : Volume d'opportunités
""")

# Statistiques générales
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Nombre total de joueurs", len(df))
    
with col2:
    buts_totaux = df['Gls'].sum()
    st.metric("Buts totaux dans le dataset", int(buts_totaux))
    
with col3:
    meilleur_buteur = classement_avance.iloc[0]['Player']
    buts_meilleur = classement_avance.iloc[0]['Gls']
    st.metric("Meilleur buteur", f"{meilleur_buteur} ({buts_meilleur} buts)")