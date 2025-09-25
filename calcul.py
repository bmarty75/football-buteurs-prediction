import streamlit as st
import pandas as pd
import numpy as np

# Déclaration globale de kagglehub
try:
    import kagglehub
    from kagglehub import KaggleDatasetAdapter
except ImportError:
    st.error("Le module kagglehub n'est pas installé. Installez-le avec : pip install kagglehub[pandas-datasets]")
    kagglehub = None


def main_application():
    """L'application principale après paiement"""
    st.title("⚽ FootAnalyst Pro - Tableau de bord")
    
    # En-tête avec infos utilisateur
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Abonnement", st.session_state.get("plan", "Aucun"))
    with col2:
        st.metric("Email", st.session_state.get("user_email", "Non défini"))
    with col3:
        if st.button("🚪 Déconnexion"):
            st.session_state.paid = False
            st.rerun()
    
    st.markdown("---")
    
    # Charger les données
    df = load_data()

    if df.empty:
        st.error("Aucune donnée n'a pu être chargée. Vérifiez la source des données.")
        st.stop()

    # Vérification des colonnes nécessaires
    colonnes_obligatoires = ['Player','Squad', 'Gls', 'MP', 'Sh', 'xG']
    colonnes_manquantes = [col for col in colonnes_obligatoires if col not in df.columns]

    if colonnes_manquantes:
        st.error(f"Colonnes manquantes : {', '.join(colonnes_manquantes)}")
        st.stop()

    # Sidebar pour les contrôles
    st.sidebar.header("Paramètres d'affichage")
    nombre_joueurs = st.sidebar.slider("Nombre de joueurs à afficher", 5, 50, 10)

    # Calculs statistiques
    df['ratio_buts_par_match'] = df['Gls'] / df['MP']
    df['ratio_buts_par_tir'] = df['Gls'] / df['Sh']
    df['tirs_par_match'] = df['Sh'] / df['MP']
    df['xG_par_match'] = df['xG'] / df['MP']

    # Nettoyage valeurs infinies
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    # Probabilité de buteur
    df['perf_off'] = (
        df['xG_par_match'] * 0.4 + 
        df['ratio_buts_par_tir'] * 0.25 + 
        df['ratio_buts_par_match'] * 0.2 + 
        df['tirs_par_match'] * 0.15
    )

    # Classement avancé
    classement_avance = df.sort_values(
        by=['perf_off', 'xG_par_match', 'xG', 'ratio_buts_par_tir', 'ratio_buts_par_match', 'tirs_par_match', 'Gls'], 
        ascending=False
    )

    # Formatage
    df_display = classement_avance.copy()
    for col in ['perf_off', 'xG_par_match', 'ratio_buts_par_tir', 'ratio_buts_par_match', 'tirs_par_match']:
        df_display[col] = df_display[col].round(3 if col != 'perf_off' else 2)

    # Affichage du top joueurs
    st.subheader(f"Top {nombre_joueurs} des buteurs les plus probables")
    colonnes_a_afficher = ['Player','Squad', 'Gls','MP','perf_off', 'xG_par_match','xG','ratio_buts_par_tir', 'ratio_buts_par_match', 'tirs_par_match']
    colonnes_disponibles = [col for col in colonnes_a_afficher if col in df_display.columns]

    st.dataframe(df_display[colonnes_disponibles].head(nombre_joueurs), use_container_width=True, height=400)

    # Bouton refresh
    if st.button('🔄 Rafraîchir les données'):
        st.cache_data.clear()
        # Supprimer le cache Kaggle pour forcer un nouveau téléchargement
        import shutil, os
        kaggle_cache = os.path.expanduser("~/.kagglehub")
        if os.path.exists(kaggle_cache):
            shutil.rmtree(kaggle_cache)
        st.rerun()

    # Infos sidebar
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
        st.metric("Buts totaux dans le dataset", int(df['Gls'].sum()))
        
    with col3:
        meilleur_buteur = classement_avance.iloc[0]['Player']
        buts_meilleur = classement_avance.iloc[0]['Gls']
        st.metric("Meilleur buteur", f"{meilleur_buteur} ({buts_meilleur} buts)")


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
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            st.error(f"Impossible de charger le fichier CSV : {e}")
            df = pd.DataFrame()
    
    return df
