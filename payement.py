import streamlit as st
def check_payment():
    """Vérifie si l'utilisateur a payé"""
    if "paid" not in st.session_state:
        st.session_state.paid = False
    
    # Initialiser les autres variables pour éviter les erreurs
    if "plan" not in st.session_state:
        st.session_state.plan = "Aucun"
    if "user_email" not in st.session_state:
        st.session_state.user_email = "Non défini"
    if "access_code" not in st.session_state:
        st.session_state.access_code = ""
    
    # Si déjà payé, on laisse passer
    if st.session_state.paid:
        return True
    
    # Sinon, afficher la page de paiement
    show_payment_page()
    return False


def show_payment_page():
    """Affiche la page de paiement/accès"""
    st.title("🔒 FootAnalyst Pro - Accès Premium")
    
    st.markdown("""
    ## 🏆 Accédez à l'analyse avancée des buteurs
    
    **Fonctionnalités incluses :**
    ✅ Analyse en temps réel des statistiques  
    ✅ Prédictions de performances  
    ✅ Données exclusives 2025-2026  
    ✅ Support prioritaire  
    """)
    
    # Options d'abonnement
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("💳 1 Jour")
        st.write("**4,99€** - Test complet")
        if st.button("Acheter 1 jour", key="1day"):
            show_payment_form("1 jour - 4,99€")
    
    with col2:
        st.subheader("🚀 1 Mois")
        st.write("**9,99€** - Meilleure valeur")
        if st.button("Acheter 1 mois", key="1month"):
            show_payment_form("1 mois - 9,99€")
    
    with col3:
        st.subheader("🏅 1 An")
        st.write("**99,99€** - Économique")
        if st.button("Acheter 1 an", key="1year"):
            show_payment_form("1 an - 99,99€")
    
    # Section code d'accès (pour les tests)
    with st.expander("🧪 Accès Développeur (Test)"):
        st.info("Utilisez ce code pour tester : **TEST123**")
        test_code = st.text_input("Code d'accès test :")
        
        if st.button("Valider le code test"):
            if test_code == "TEST123":
                st.session_state.paid = True
                st.session_state.access_code = "TEST123"
                st.success("Accès développeur activé !")
                st.rerun()
            else:
                st.error("Code invalide")

def show_payment_form(plan):
    """Affiche le formulaire de paiement"""
    st.subheader(f"Paiement - {plan}")
    
    with st.form("payment_form"):
        email = st.text_input("📧 Email de réception")
        card_number = st.text_input("💳 Numéro de carte", placeholder="1234 5678 9012 3456")
        exp_date = st.text_input("📅 Expiration (MM/AA)", placeholder="12/25")
        cvc = st.text_input("🔒 CVC", placeholder="123")
        
        if st.form_submit_button("Payer maintenant"):
            # Simulation de paiement réussi
            process_payment(email, plan)

def process_payment(email, plan):
    """Traite le paiement (simulation)"""
    with st.spinner("Traitement du paiement..."):
        time.sleep(2)  # Simulation traitement
        
        # Générer un code d'accès unique
        access_code = f"FOOT{int(time.time())}"
        VALID_CODES[access_code] = {"used": False, "created": datetime.now()}
        
        st.session_state.paid = True
        st.session_state.access_code = access_code
        st.session_state.user_email = email
        st.session_state.plan = plan
        
        st.success(f"✅ Paiement accepté ! Code d'accès : {access_code}")
        st.info("📧 Un email de confirmation a été envoyé")
        
        st.rerun()