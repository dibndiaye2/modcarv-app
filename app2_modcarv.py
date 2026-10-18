import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import gdown

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(page_title="MODCARV", page_icon="📊", layout="wide")

# ============================================================
# TÉLÉCHARGEMENT DES DONNÉES DEPUIS GOOGLE DRIVE
# ============================================================
ID_MENAGE = "1dDQ_FHMqCIhYeeXWy0VtytRv-5ufbEmO"
ID_INDIVIDU = "1wis78AETHAhm7SrvzPjmRpqqC4f1E6bv"
ID_MESURE = "1N2VFB_oJ99ARr8veMBiU2SPCf4elbf55"

@st.cache_data
def charger_donnees():
    dossier = Path("data")
    dossier.mkdir(exist_ok=True)
    
    fichiers = {
        'consolide_menage.parquet': ID_MENAGE,
        'consolide_individu.parquet': ID_INDIVIDU,
        'consolide_mesure_enrichie.parquet': ID_MESURE
    }
    
    for nom, file_id in fichiers.items():
        chemin = dossier / nom
        if not chemin.exists():
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, str(chemin), quiet=False)
            
    menage = pd.read_parquet(dossier / 'consolide_menage.parquet')
    patient = pd.read_parquet(dossier / 'consolide_individu.parquet')
    mesure = pd.read_parquet(dossier / 'consolide_mesure_enrichie.parquet')
    
    # Correspondance des noms de zones
    CORRESPONDANCE_ZONES = {
        '01': 'Langue de Barbarie', '02': 'Île', '03': 'Sor 1', '04': 'Sor 2',
        '05': 'Ngallele', '06': 'Pikine', '07': 'Mpal', '08': 'Gandiol'
    }
    if 'zone' in menage.columns:
        menage['zone_str'] = menage['zone'].astype(str).str.strip()
        menage['zone_nom'] = menage['zone_str'].map(CORRESPONDANCE_ZONES).fillna(menage['zone_str'])
    
    return menage, patient, mesure

with st.spinner("Chargement des données..."):
    try:
        menage, patient, mesure = charger_donnees()
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        st.stop()

# ============================================================
# MENU LATERAL
# ============================================================
st.sidebar.title("📊 MODCARV")
st.sidebar.markdown("*Tableaux de bord décisionnels*")
st.sidebar.markdown("---")

choix = st.sidebar.radio(
    "**Choisir un tableau de bord :**",
    ["🏠 Accueil",
     "📊 D1 — Suivi de la collecte",
     "🌍 D2 — Épidémiologie descriptive",
     "🩸 D3 — Suivi glycémique",
     "🔍 Recherche ménage",
     "📝 Évaluation"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Projet MODCARV - Saint-Louis, Sénégal")
st.sidebar.caption("Dib NDIAYE — Master SID UADB")

# ============================================================
# PAGE ACCUEIL
# ============================================================
# ============================================================
# PAGE ACCUEIL
# ============================================================
if choix == "🏠 Accueil":
    st.title("📊 Tableaux de bord MODCARV")
    st.markdown("*Projet MODCARV — Saint-Louis, Sénégal*")
    st.markdown("---")

    st.markdown("""
    ### Bienvenue
    Ce dispositif comprend **trois tableaux de bord** et des modules complémentaires :
    """)
    
    st.table(pd.DataFrame({
        "Dashboard": ["📊 D1 — Collecte", "🌍 D2 — Épidémiologie", "🩸 D3 — Glycémie"],
        "Utilisateurs": ["Superviseurs terrain", "Coordination médicale", "Médecin référent"],
        "Objectif": ["Suivi de la collecte", "Prévalences + résultats", "Suivi patients"]
    }))

    st.markdown("---")
    st.subheader("Chiffres clés")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Patients", f"{len(patient)}")
    c2.metric("🏠 Ménages", f"{len(menage)}")
    c3.metric("🧪 Prélèvements", "460")
    c4.metric("✅ Rattachements", "453")

    st.markdown("---")
    st.markdown("### 🎯 Que pouvez-vous faire avec cet outil ?")
    st.markdown("En plus des tableaux de bord, cette application met à votre disposition **deux fonctionnalités complémentaires** :")
    st.markdown("**🔍 Recherche par ménage** : Consultez rapidement le profil de risque cardiovasculaire d'un ménage donné.")
    st.markdown("**📝 Formulaire d'évaluation** : Donnez votre avis à la fin de l'exploration de l'outil.")

    st.markdown("---")
    st.markdown("### 📖 Dictionnaire des sigles et variables")
    
    # Le dictionnaire (bien aligné avec 4 espaces)
    dico_data = pd.DataFrame({
        "Sigle / Terme": [
            "ATCD", "HTA", "IMC", "GPAQ", "SF-36", "ICC", 
            "Prélèvements", "Rattachements", 
            "pct_hta", "pct_diabete", "pct_surpoids"
        ],
        "Signification": [
            "Antécédent (ex: ATCD familial = antécédent dans la famille)",
            "Hypertension Artérielle",
            "Indice de Masse Corporelle",
            "Global Physical Activity Questionnaire (activité physique)",
            "Questionnaire de qualité de vie (36 questions)",
            "Coefficient de Corrélation Intra-Classe",
            "460 : Nombre total de prélèvements collectés",
            "453 : Prélèvements liés à un patient après nettoyage",
            "Prévalence de HTA mesurée dans la zone (%)",
            "Prévalence du Diabète connu dans la zone (%)",
            "Prévalence du Surpoids ou de Obésité dans la zone (%)"
        ]
    })
    st.dataframe(dico_data, use_container_width=True, hide_index=True)

# ============================================================
# PAGE D1 — COLLECTE
# ============================================================
elif choix == "📊 D1 — Suivi de la collecte":
    st.title("📊 Dashboard D1 — Suivi de la collecte")
    st.markdown("*Projet MODCARV — Saint-Louis, Sénégal*")
    st.markdown("---")

    st.header("1. Indicateurs clés")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Patients", f"{len(patient)}")
    c2.metric("🏠 Ménages", f"{len(menage)}")
    c3.metric("🧪 Prélèvements", "460")
    c4.metric("✅ Rattachements", "453")

    st.markdown("---")
    st.header("2. Avancement par zone")
    if "zone_nom" in menage.columns:
        zc = menage.groupby("zone_nom").size().reset_index(name="nb").sort_values("nb", ascending=False)
        fig = px.bar(zc, x="zone_nom", y="nb", color="nb", color_continuous_scale="Viridis",
                     labels={"zone_nom": "Zone géographique", "nb": "Nombre de ménages"})
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("3. Taux de complétude")
    variables = ["age_calculee", "Sexe", "IMC", "hypertension", "hta_connue",
                 "diabete_connu", "gpaq_inactif", "sf_PCS", "sf_MCS", "af_hta"]
    variables = [v for v in variables if v in patient.columns]
    cplt = [{"Variable": v, "Valides": int(patient[v].notna().sum()), "Total": len(patient), "Complétude (%)": round(patient[v].notna().sum() / len(patient) * 100, 1)} for v in variables]
    st.dataframe(pd.DataFrame(cplt), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.header("4. Alertes et points de vigilance")
    st.subheader("✅ Exclusions protocolaires (attendues)")
    ca, cb = st.columns(2)
    n_age = int(patient["age_calculee"].isna().sum()) if "age_calculee" in patient.columns else 0
    n_imc = int(patient["IMC"].isna().sum()) if "IMC" in patient.columns else 0
    ca.info(f"**{n_age} patients sans âge** — enfants < 18 ans exclus")
    cb.info(f"**{n_imc} patients sans IMC** — mêmes enfants exclus")
    
    st.subheader("⚠️ Points de vigilance")
    st.warning("**7 prélèvements non rattachés** — patients non enrôlés ou codes ambigus")
    st.warning("**103 patients non prélevés** — sans échantillon biologique (non éligibles ou refus), ce qui est normal et documenté")
    
    st.subheader("📌 Informations")
    n_hta = int(patient["hypertension"].sum()) if "hypertension" in patient.columns else 0
    st.info(f"**{n_hta} cas d'HTA mesurée** dans la population")

# ============================================================
# PAGE D2 — ÉPIDÉMIOLOGIE
# ============================================================
elif choix == "🌍 D2 — Épidémiologie descriptive":
    st.title("🌍 Dashboard D2 — Épidémiologie descriptive")
    st.markdown("---")

    st.header("1. Prévalences principales")
    c1, c2, c3, c4 = st.columns(4)
    n = int(patient["hypertension"].sum()) if "hypertension" in patient.columns else 0
    c1.metric("🩺 HTA mesurée", f"{n}", f"{n/len(patient)*100:.1f} %")
    n = int(patient["diabete_connu"].sum()) if "diabete_connu" in patient.columns else 0
    c2.metric("🩸 Diabète connu", f"{n}", f"{n/len(patient)*100:.1f} %")
    if "hyperglycemie" in patient.columns:
        nv = int(patient["hyperglycemie"].notna().sum())
        n = int(patient["hyperglycemie"].sum())
        c3.metric("📊 Hyperglycémie", f"{n}", f"{n/nv*100:.1f} %" if nv > 0 else "—")
    n = int(patient["surpoids_ou_obesite"].sum()) if "surpoids_ou_obesite" in patient.columns else 0
    c4.metric("⚖️ Surpoids/Obésité", f"{n}", f"{n/len(patient)*100:.1f} %")

    c5, c6, c7, c8 = st.columns(4)
    n = int(patient["hta_connue"].sum()) if "hta_connue" in patient.columns else 0
    c5.metric("📋 HTA connue", f"{n}", f"{n/len(patient)*100:.1f} %")
    n = int(patient["fumeur_actuel"].sum()) if "fumeur_actuel" in patient.columns else 0
    c6.metric("🚬 Fumeurs", f"{n}", f"{n/len(patient)*100:.1f} %")
    n = int(patient["gpaq_inactif"].sum()) if "gpaq_inactif" in patient.columns else 0
    c7.metric("🛋️ Inactifs", f"{n}", f"{n/len(patient)*100:.1f} %")
    n = int(patient["obesite"].sum()) if "obesite" in patient.columns else 0
    c8.metric("⚖️ Obésité", f"{n}", f"{n/len(patient)*100:.1f} %")

    st.markdown("---")
    st.header("2. Signes d'appel et antécédents familiaux")
    c1, c2, c3, c4 = st.columns(4)
    if "a_signes_appel" in patient.columns:
        n = int(patient["a_signes_appel"].sum())
        c1.metric("🩺 Au moins 1 signe", f"{n}", f"{n/len(patient)*100:.1f} %")
    if "a_fatigue_chronique" in patient.columns:
        n = int(patient["a_fatigue_chronique"].sum())
        c2.metric("😴 Fatigue chronique", f"{n}", f"{n/len(patient)*100:.1f} %")
    if "a_troubles_visuels" in patient.columns:
        n = int(patient["a_troubles_visuels"].sum())
        c3.metric("👁️ Troubles visuels", f"{n}", f"{n/len(patient)*100:.1f} %")
    if "a_polyurie" in patient.columns:
        n = int(patient["a_polyurie"].sum())
        c4.metric("💧 Polyurie", f"{n}", f"{n/len(patient)*100:.1f} %")

    c5, c6, c7, c8 = st.columns(4)
    if "af_hta" in patient.columns:
        n = int(patient["af_hta"].sum())
        c5.metric("🧬 ATCD fam. HTA", f"{n}", f"{n/len(patient)*100:.1f} %")
    if "af_diabete" in patient.columns:
        n = int(patient["af_diabete"].sum())
        c6.metric("🧬 ATCD fam. Diabète", f"{n}", f"{n/len(patient)*100:.1f} %")
    if "af_obesite" in patient.columns:
        n = int(patient["af_obesite"].sum())
        c7.metric("🧬 ATCD fam. Obésité", f"{n}", f"{n/len(patient)*100:.1f} %")
    if "a_traitement_en_cours" in patient.columns:
        n = int(patient["a_traitement_en_cours"].sum())
        c8.metric("💊 Traitement en cours", f"{n}", f"{n/len(patient)*100:.1f} %")

    if "nb_signes_appel" in patient.columns:
        st.markdown("**Distribution du nombre de signes d'appel :**")
        vc = patient["nb_signes_appel"].value_counts().sort_index().reset_index()
        vc.columns = ["Nb signes", "Patients"]
        fig = px.bar(vc, x="Nb signes", y="Patients", color="Patients", color_continuous_scale="Reds")
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("3. Répartition démographique")
    ca, cb = st.columns(2)
    with ca:
        if "Sexe" in patient.columns:
            s = patient["Sexe"].value_counts().reset_index()
            s.columns = ["Sexe", "Nb"]
            fig = px.pie(s, values="Nb", names="Sexe", color_discrete_sequence=["#ff7f0e", "#1f77b4"], title="Répartition par sexe")
            st.plotly_chart(fig, use_container_width=True)
    with cb:
        if "age_calculee" in patient.columns:
            fig = px.histogram(patient["age_calculee"].dropna(), nbins=20, color_discrete_sequence=["#2e75b6"], title="Distribution de l'âge")
            fig.update_layout(xaxis_title="Âge (années)", yaxis_title="Nombre de patients", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("4. Prévalences par zone")
    if "zone_nom" in menage.columns:
        pz = patient.merge(menage[["code_famille_norm", "zone_nom"]], on="code_famille_norm", how="left")
        prev = pz.groupby("zone_nom").agg(
            n=("code_patient_norm", "count"),
            pct_hta=("hypertension", lambda x: x.mean() * 100 if x.notna().any() else 0),
            pct_diabete=("diabete_connu", lambda x: x.mean() * 100 if x.notna().any() else 0),
            pct_surpoids=("surpoids_ou_obesite", lambda x: x.mean() * 100 if x.notna().any() else 0)
        ).round(1).reset_index()
        st.dataframe(prev, use_container_width=True, hide_index=True)

        fig = px.bar(prev, x="zone_nom", y=["pct_hta", "pct_diabete", "pct_surpoids"], barmode="group",
                     color_discrete_sequence=["#d62728", "#ff7f0e", "#2ca02c"],
                     labels={"zone_nom": "Zone géographique", "value": "Prévalence (%)", "variable": "Indicateur"})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.header("5. Profils de risque ménage")
    if "profil_risque" in menage.columns:
        pc = menage["profil_risque"].value_counts().reset_index()
        pc.columns = ["Profil", "Nb"]
        ordre = ["Faible risque", "Risque modere", "Risque eleve"]
        pc["Profil"] = pd.Categorical(pc["Profil"], categories=ordre, ordered=True)
        pc = pc.sort_values("Profil")

        ca, cb = st.columns([1, 2])
        with ca:
            st.dataframe(pc, use_container_width=True, hide_index=True)
        with cb:
            fig = px.bar(pc, x="Profil", y="Nb", color="Profil",
                        color_discrete_map={"Faible risque": "#2ca02c", "Risque modere": "#ff7f0e", "Risque eleve": "#d62728"})
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

        st.info("""
        **ℹ️ Note sur le calcul du score de risque**
        Le score de risque de chaque ménage est calculé comme la **moyenne des z-scores** de sept variables (sédentarité, environnement, hyperglycémie, diabète, SF-36 PCS, SF-36 MCS, antécédents familiaux), extraites des modèles multiniveaux nuls.
        Les 103 ménages sont classés en **3 terciles** : 🟢 Faible risque (1er tercile), 🟠 Risque modéré (2e tercile), 🔴 Risque élevé (3e tercile).
        Ce score permet de classer les ménages pour prioriser les interventions. Ce n'est **pas une probabilité** de survenue d'un événement cardiovasculaire.

        **💡 Interprétation :**
        La répartition des ménages est **équilibrée** (environ 1/3 par profil). Cela confirme la robustesse du classement.
        Les ménages du profil "Risque élevé" (en rouge) cumulent les facteurs de risque comportementaux (inactivité, environnement défavorable) et métaboliques (hyperglycémie, diabète).
        Ils constituent la **cible prioritaire** pour les campagnes de prévention du projet MODCARV.
        """)

    st.markdown("---")
    st.header("6. Principaux résultats statistiques")
    st.markdown("*Synthèse des résultats d'analyse du risque cardiovasculaire*")
    
    st.subheader("6.1 Top 11 des facteurs à forte composante ménage (H1)")
    icc_top = pd.DataFrame({
        'Facteur': ['Traitement en cours', 'Au moins 1 signe d\'appel', 'Environnement', 'Sédentarité', 'Hyperglycémie', 'Nb signes d\'appel', 'ATCD familial diabète', 'ATCD familial obésité', 'Inactif (GPAQ)', 'Diabète connu', 'Nb types ATCD'],
        'ICC': [0.686, 0.517, 0.498, 0.489, 0.429, 0.342, 0.274, 0.255, 0.230, 0.219, 0.210]
    }).sort_values('ICC', ascending=True)

    fig = px.bar(icc_top, x='ICC', y='Facteur', orientation='h', color='ICC', color_continuous_scale='Reds', title='ICC des 11 facteurs à composante ménage forte (ICC > 0,20)')
    fig.update_layout(height=450, showlegend=False)
    fig.add_vline(x=0.20, line_dash='dash', line_color='red')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("6.2 Mécanismes — Effet de composition vs contexte (H2)")
    h2_data = pd.DataFrame({
        'Facteur': ['Diabète', 'Sédentarité', 'Environnement'],
        'Réduction (%)': [62.7, 31.4, 5.2],
        'Interprétation': ['Composition (génétique)', 'Mixte', 'Contexte pur']
    })
    ca, cb = st.columns([1, 1])
    with ca:
        st.dataframe(h2_data, use_container_width=True, hide_index=True)
    with cb:
        fig = px.bar(h2_data, x='Facteur', y='Réduction (%)', color='Interprétation',
                     color_discrete_map={'Composition (génétique)': '#d62728', 'Mixte': '#ff7f0e', 'Contexte pur': '#2ca02c'})
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("6.3 Découverte H4 — Conscience du risque")
    st.info("""
    **L'ATCD familial est un marqueur de CONSCIENCE du risque, pas de prédisposition biologique.**
    - ATCD HTA → HTA connue : **p = 0,0014** ✅ (prédit le diagnostic)
    - ATCD HTA → HTA mesurée : **p = 1,00** ❌ (ne prédit pas la prévalence réelle)
    - Sous-diagnostic : 58,2 % (sans ATCD) vs 41,6 % (avec ATCD)
    **Recommandation :** cibler les campagnes de sensibilisation sur les personnes SANS ATCD familial connu.
    """)

# ============================================================
# PAGE D3 — GLYCÉMIE
# ============================================================
elif choix == "🩸 D3 — Suivi glycémique":
    st.title("🩸 Dashboard D3 — Suivi glycémique")
    st.markdown("---")

    st.header("1. Indicateurs clés")
    c1, c2, c3, c4 = st.columns(4)
    n_pat = mesure["code_patient_norm"].nunique() if "code_patient_norm" in mesure.columns else 0
    c1.metric("👥 Patients prélevés", f"{n_pat}")
    c2.metric("🧪 Mesures", f"{len(mesure)}")
    n_multi = (mesure.groupby("code_patient_norm").size() >= 2).sum() if "code_patient_norm" in mesure.columns else 0
    c3.metric("🔁 Patients ≥ 2 mesures", f"{n_multi}")
    if "glycemie" in mesure.columns:
        c4.metric("📊 Glycémie médiane", f"{mesure['glycemie'].median():.2f} g/L")

    st.markdown("---")
    st.header("2. Distribution par fenêtre")
    st.info("**Fenêtres de collecte :** F1 (juin-juillet 2025) • F2 (déc. 2025-fév. 2026) • F3 (mars-avril 2026)")
    if "fenetre" in mesure.columns and "glycemie" in mesure.columns:
        fig = px.box(mesure.dropna(subset=["glycemie"]), x="fenetre", y="glycemie", color="fenetre",
                     color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **💡 Interprétation :** 
        La distribution de la glycémie montre une **médiane relativement stable** autour de 0,95 g/L à travers les fenêtres (F1, F2, F3). 
        Cependant, on observe une **plus grande dispersion (valeurs extrêmes plus élevées)** lors de la campagne initiale (F1) par rapport aux suivis (F2 et F3). 
        Cela suggère que les patients dépistés lors de la première vague présentaient des glycémies plus hétérogènes, tandis que les suivis semblent indiquer une certaine stabilisation.
        """)

    st.markdown("---")
    st.header("3. Hyperglycémie par fenêtre")
    if "fenetre" in mesure.columns and "glycemie" in mesure.columns:
        m = mesure.dropna(subset=["glycemie"]).copy()
        m["hyper"] = (m["glycemie"] >= 1.26).astype(int)
        hf = m.groupby("fenetre").agg(n=("hyper", "count"), n_hyper=("hyper", "sum"), pct=("hyper", lambda x: x.mean() * 100)).round(1).reset_index()
        st.dataframe(hf, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.header("4. Distribution par rang")
    st.info("Le **rang** correspond à l'ordre chronologique de la mesure pour un même patient : Rang 1 (première mesure), Rang 2 (deuxième mesure), etc.")
    if "rang" in mesure.columns and "glycemie" in mesure.columns:
        fig = px.box(mesure.dropna(subset=["glycemie"]), x="rang", y="glycemie")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        **💡 Interprétation :** 
        L'évolution par rang montre que la **médiane de la glycémie reste stable** (autour de 0,95 g/L) entre la 1ère et la 5ème mesure. 
        Cependant, la variance (la taille de la boîte) a tendance à **se réduire** au fil des mesures. 
        Cela pourrait refléter un effet de **régression vers la moyenne** : les patients avec des glycémies initialement très élevées ont été pris en charge, ramenant leurs valeurs vers la moyenne de la cohorte lors des mesures suivantes.
        """)

    st.markdown("---")
    st.header("5. Vue individuelle (pseudonymisée)")
    st.warning("⚠️ Accès réservé au personnel médical habilité")
    st.info("Cette vue affiche la **glycémie moyenne** d'un patient donné, calculée sur l'ensemble de ses prélèvements. Le filtre par **profil de risque du ménage** permet de concentrer l'analyse sur les patients des ménages à risque élevé.")

    if "profil_risque" in mesure.columns:
        st.markdown("**Filtrer par profil de risque du ménage :**")
        profil_filtre = st.selectbox("Profil", ["Tous", "Faible risque", "Risque modere", "Risque eleve"])
        mesure_filtree = mesure[mesure["profil_risque"] == profil_filtre] if profil_filtre != "Tous" else mesure
    else:
        mesure_filtree = mesure

    if "code_patient_norm" in mesure_filtree.columns:
        liste = sorted(mesure_filtree["code_patient_norm"].dropna().unique())
        if len(liste) > 0:
            p = st.selectbox("Choisir un patient :", liste)
            if p:
                sub = mesure_filtree[mesure_filtree["code_patient_norm"] == p].sort_values("date_mesure")
                st.dataframe(sub[["date_mesure", "rang", "glycemie", "duree_jeune_h", "fenetre"]], use_container_width=True, hide_index=True)
                
                if len(sub) > 1:
                    fig = px.line(sub, x="date_mesure", y="glycemie", markers=True, title=f"Trajectoire glycémique du patient {p}")
                    fig.add_hline(y=1.26, line_dash="dash", line_color="red", annotation_text="Seuil hyperglycémie (1.26 g/L)")
                    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE RECHERCHE MÉNAGE
# ============================================================
elif choix == "🔍 Recherche ménage":
    st.title("🔍 Recherche d'un ménage par code famille")
    st.markdown("---")
    
    codes_disponibles = sorted(menage['code_famille_norm'].dropna().unique().tolist()) if 'code_famille_norm' in menage.columns else []
    
    col1, col2 = st.columns([3, 1])
    with col1:
        code_saisi = st.selectbox("Code famille :", options=[""] + codes_disponibles)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        bouton = st.button("🔎 Rechercher", use_container_width=True)
        
    if bouton and code_saisi:
        res = menage[menage['code_famille_norm'] == code_saisi]
        if not res.empty:
            m = res.iloc[0]
            profil = str(m.get('profil_risque', '')).strip()
            
            if 'eleve' in profil.lower(): couleur, emoji = '#E74C3C', '🔴'
            elif 'modere' in profil.lower(): couleur, emoji = '#F39C12', '🟠'
            else: couleur, emoji = '#27AE60', '🟢'
            
            st.markdown(f"""
            <div style="background-color: {couleur}; padding: 20px; border-radius: 10px; text-align: center; color: white;">
                <h2>{emoji} Profil : {profil}</h2>
                <p>Ce ménage présente un risque cardiovasculaire {profil.lower()}.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📊 Informations du ménage")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Score de risque", f"{m.get('score_menage', 0):.3f}")
            c2.metric("Patients", int(m.get('nb_patients', 0)))
            c3.metric("Commune", str(m.get('Commune', 'Saint-Louis')))
            c4.metric("Zone", str(m.get('zone_nom', m.get('zone', 'N/A'))))
            
            st.info("""
            **ℹ️ Note : le score de risque** est calculé à partir de sept variables (sédentarité, environnement, hyperglycémie, diabète, SF-36 PCS, SF-36 MCS, antécédents familiaux), selon la méthode décrite au chapitre 4 du mémoire.
            """)
        else:
            st.error("Ménage non trouvé.")

# ============================================================
# PAGE ÉVALUATION
# ============================================================
elif choix == "📝 Évaluation":
    st.title("📝 Évaluation de l'application MODCARV")
    st.markdown("---")
    st.markdown("""
    ### Votre avis compte !
    Ce questionnaire a pour objectif d'évaluer votre satisfaction et l'utilisabilité 
    des tableaux de bord MODCARV (Collecte, Épidémiologie, Glycémie, Recherche ménage).
    
    Vos retours nous aideront à améliorer l'outil pour mieux répondre à vos besoins 
    sur le terrain. Le temps de réponse est estimé à **2 minutes**.
    """)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSfM2ReK2Gf25TSMhwtXiSymBc9yoNgC3pGHhFmpchq89KutmQ/viewform" 
           target="_blank"
           style="background-color: #FF9800; color: white; padding: 15px 40px; 
                  font-size: 18px; text-decoration: none; border-radius: 8px; font-weight: bold;">
            📋 Répondre au questionnaire
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Le questionnaire s'ouvrira dans un nouvel onglet de votre navigateur.")


   
