import streamlit as st
import payement as pay
import calcul as calc
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="FootAnalyst Pro", layout="wide")

# Codes d'accès (à gérer plus tard avec une base de données)
VALID_CODES = {
    "PREMIUM2024": {"used": False, "created": datetime.now()},
    "FOOTBALLPRO": {"used": False, "created": datetime.now()}
}


def main():
    """Fonction principale"""
    # Vérifier le paiement avant tout
    # if not pay.check_payment():
    #    return  # Arrête l'exécution si pas payé
    
    # Si payé, afficher l'application
    calc.main_application()

if __name__ == "__main__":
    main()