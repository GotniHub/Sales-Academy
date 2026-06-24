import streamlit as st
import pandas as pd
import io
from streamlit_option_menu import option_menu
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from PIL import Image  # ← tu dois avoir cette ligne


# 👇 AJOUTE LE CODE DU LOGO ICI
logo = Image.open("Logo Sales Academy.png")

# --- NAVBAR ---
with st.container():
    col1, col2 = st.columns([2, 12])
    with col1:
        st.image(logo, width=180)
    with col2:
        selected = option_menu(
            menu_title=None,
            options=["Importation & Calculs","RAPPORT FINANCE","RAPPORT CLIENT"],
            icons=["upload", "bar-chart-line", "briefcase", "cash-stack", "file-earmark-text"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "nav-link-selected": {"background-color": "#0033A0", "color": "white"},
            }
        )

st.markdown("""
<style>
/* Modifier les unités sélectionnées dans le multiselect */
[data-baseweb="tag"] {
    background-color: #0033A0 !important;
    color: white !important;
    font-weight: bold;
    border-radius: 0.5rem;
    padding: 5px;
}
</style>
            
""", unsafe_allow_html=True)
def custom_round(value):
    # Arrondi spécifique : 0.25 → 0.5, 0.75 → 1.0, 1.25 → 1.5, etc.
    remainder = value % 0.5
    if remainder == 0.25:
        return value + 0.25
    elif remainder == 0.75:
        return value + 0.25
    else:
        return value

# Données par défaut pour FORMATION et PREPA
formation_prepa_data = {
    0.5: 0.25,
    1.0: 0.5,
    1.5: 0.75,
    2.0: 1.0,
    2.5: 1.25,
    3.0: 1.0,

    # Ajoutez plus de cas si nécessaire
}

# Données par défaut pour PU par formateur
pu_data = {
    "stéphane pean": 400,
    "julie larue": 650,
    "dennis comunian": 400,
    "norbert macia": 533.33,
    "toshihiko ikezaki": 600,
    "béatrice chausson": 600,
    "pauline chouvet": 400,
    "alejandra rosquin": 360,
    "thierry riva": 1500,
    "kostas tzentzeras": 400,
    "norbert macia_ta&prod": 400,
    "cédric jumel": 800,
    "jean philippe rost": 900,
    "amine aboughalem": 400,
}

# Données par défaut pour PU / FORMATION en fonction de la Population (pour 1.5 jours)
population_pu_data = {
    "sales team": 3500,
    "kam": 4000,
    "manager": 4000,
    "mm": 4000,
    "all": 4000,
    "direction": 4000,
    # Ajoutez plus de populations si nécessaire
}

# Données CA pour TA (Budget par type de TA)
ta_budget_data = {
    "observation": 1000,
    "suivi & contrôle": 1000
}

if selected == "Importation & Calculs":

    st.title("Importation & Calculs")

    # Fonction pour modifier les données dans la sidebar
    def modify_data_in_sidebar(default_formation_prepa, default_pu, default_population_pu):
        st.sidebar.header("Modifier les Données")
        
        # Modifier les données de FORMATION et PREPA
        st.sidebar.subheader("Données FORMATION et PREPA")
        modified_formation_prepa = {}
        for formation, prepa in default_formation_prepa.items():
            modified_formation_prepa[formation] = st.sidebar.number_input(
                f"PREPA pour FORMATION {formation} jours", value=prepa
            )
        
        # Modifier les données de PU par formateur
        st.sidebar.subheader("PU par Formateur")
        modified_pu_data = {}
        for formateur, pu in default_pu.items():
            modified_pu_data[formateur] = st.sidebar.number_input(
                f"PU pour {formateur.capitalize()}", value=pu
            )
        
        # Modifier les données de PU par Population
        st.sidebar.subheader("PU par Population")
        modified_population_pu = {}
        for population, pu in default_population_pu.items():
            modified_population_pu[population] = st.sidebar.number_input(
                f"PU pour {population.capitalize()}", value=pu
            )
        
        return modified_formation_prepa, modified_pu_data, modified_population_pu

    # Normaliser les clés de pu_data
    #normalized_pu_data = {k.strip().lower(): v for k, v in pu_data.items()}


    # Fonction pour récupérer la valeur de PREPA en fonction de FORMATION
    def get_prepa_value(nombre_de_jour):
        return formation_prepa_data.get(nombre_de_jour, 0)  # Retourne 0 si la valeur n'est pas trouvée

    # Fonction pour récupérer le PU en fonction du formateur
    def get_pu_value(formateur):
        return pu_data.get(formateur, 0)  # Retourne 0 si le formateur n'est pas trouvé

    # Fonction pour récupérer le PU / FORMATION en fonction de la population
    def get_population_pu(population):
        return population_pu_data.get(population, 0)  # Retourne 0 si la population n'est pas trouvée

    # Fonction pour calculer les champs
    def calculate_fields_with_defaults(calendar_df):
        # Vérifiez si la colonne 'Nombre de jour' existe
        if "Nombre de jour" not in calendar_df.columns:
            st.error("La colonne 'Nombre de jour' est manquante dans le fichier calendrier.")
            return None

        # Normaliser la colonne Population
        calendar_df['Population'] = calendar_df['Population'].astype(str).str.strip().str.lower()

        # Normaliser la colonne Formateur 1
        calendar_df['Formateur 1'] = calendar_df['Formateur 1'].astype(str).str.strip().str.lower()
        
        # Conversion des colonnes numériques
        calendar_df['Nombre de jour'] = pd.to_numeric(
            calendar_df['Nombre de jour'].astype(str).str.replace(',', '.'),
            errors='coerce'
        ).fillna(0)

        # Ajout des colonnes calculées
        calendar_df['Jour arrondi'] = calendar_df['Nombre de jour'].apply(custom_round)
        calendar_df['PREPA'] = calendar_df['Jour arrondi'].map(formation_prepa_data).fillna(0)


        calendar_df['Nb jours prépa inclus'] = calendar_df['Jour arrondi'] + calendar_df['PREPA']
        # Ajout du PU par formateur
        calendar_df['PU'] = calendar_df['Formateur 1'].apply(get_pu_value)

        # Calcul du coût formateur
        calendar_df['Cout formateur'] = calendar_df['Nb jours prépa inclus'] * calendar_df['PU']

            # Calcul du CA
        def calculate_ca(row):
            pu_population = get_population_pu(row['Population'])  # PU en fonction de la population
            if pu_population == 0 or row['Jour arrondi'] == 0:
                return 0
            return (pu_population / 1.5) * row['Jour arrondi']  # CA = (PU/1.5) * Nombre de jour

        calendar_df['CA'] = calendar_df.apply(calculate_ca, axis=1)

        # Formater Cout formateur avec le signe €
        calendar_df['Cout formateur'] = calendar_df['Cout formateur'].apply(lambda x: f"{x:,.2f} €")
        calendar_df['CA'] = calendar_df['CA'].apply(lambda x: f"{x:,.2f} €")

        return calendar_df

    # Streamlit app
    st.title("Calcul des Champs avec Données par Défaut")


    # Téléchargement du fichier calendrier

    calendar_file = st.file_uploader("Téléchargez le fichier Calendrier (Test_file.xlsx)", type="xlsx")

    if calendar_file:
        # Lecture simple de la feuille sans calcul
        calendar_df = pd.read_excel(calendar_file, sheet_name="Formations 2026", header=2)
        
        st.subheader("📄 Aperçu des données importées (brutes)")
        st.dataframe(calendar_df, hide_index=True)

        # Affichage du bouton de calcul
        if st.button("🔢 Calculer les champs"):
            # Exécution du calcul et stockage dans session_state
            st.session_state["calendar_file"] = calendar_file
            st.session_state["calendar_df"] = calendar_df
            st.session_state["calcul_clicked"] = True

    # Si le bouton a déjà été cliqué, récupérer les données et afficher les résultats
    if st.session_state.get("calcul_clicked", False):
        # Rechargement fichier depuis la session si dispo
        calendar_file = st.session_state.get("calendar_file")
        calendar_df = st.session_state.get("calendar_df")

        # ✅ Formulaire dynamique affiché après calcul (si toggle activé)
        if st.sidebar.toggle("Afficher/Modifier les Données", value=False):
            formation_prepa_data, pu_data, population_pu_data = modify_data_in_sidebar(
                formation_prepa_data, pu_data, population_pu_data
            )

        # 🔁 Refaire les calculs avec les nouvelles données si modifiées
        result_df = calculate_fields_with_defaults(calendar_df)
        # 🔹 Filtres sur Résultats calculés
        if result_df is not None and "BU" in result_df.columns and "Maintenue / Annulée" in result_df.columns:
            st.subheader("🧩 Filtres sur Résultats calculés")

            bu_list = sorted(result_df["BU"].dropna().unique())
            selected_bu_calc = st.multiselect("Filtrer par BU", options=bu_list, default=bu_list, key="calc_bu")

            statut_list = sorted(result_df["Maintenue / Annulée"].dropna().unique())
            selected_statuts_calc = st.multiselect("Filtrer par Maintenue / Annulée", options=statut_list, default=statut_list, key="calc_status")
            # ✅ Nouveau filtre par Module
            if "Module" in result_df.columns:
                module_list = sorted(result_df["Module"].dropna().unique())
                selected_modules = st.multiselect("Filtrer par Module", options=module_list, default=module_list, key="calc_module")
            else:
                selected_modules = None
            # ➤ Appliquer les filtres à result_df
            result_df = result_df[
                result_df["BU"].isin(selected_bu_calc) &
                result_df["Maintenue / Annulée"].isin(selected_statuts_calc)
            ]
            if selected_modules is not None:
                result_df = result_df[result_df["Module"].isin(selected_modules)]
        st.session_state["result_df"] = result_df
        st.subheader("📄 Résultats calculés")
        st.dataframe(result_df, hide_index=True)

        # Téléchargement du fichier modifié
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False, sheet_name="Formations 2026")
        output.seek(0)

        st.download_button(
            label="💾 Télécharger le fichier modifié",
            data=output,
            file_name="Calendrier_Formateurs_Modifié.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif selected == "RAPPORT FINANCE":
    st.title("Rapport Finance - Ventilation par BU")

    # Fonction de conversion des trimestres et de "Février"
    def convert_trimestre_to_date(trimestre):
        if isinstance(trimestre, str):
            trimestre = trimestre.strip().lower()
            if trimestre == "trimestre 1":
                return pd.Timestamp("2026-01-01")
            elif trimestre == "trimestre 2":
                return pd.Timestamp("2026-04-01")
            elif trimestre == "trimestre 3":
                return pd.Timestamp("2026-07-01")
            elif trimestre == "février":
                return pd.Timestamp("2026-02-01")
            elif trimestre == "tbc":
                return pd.Timestamp("2026-12-31")
            elif trimestre == "tbc in sept-oct":
                return pd.Timestamp("2026-09-01")
        return pd.to_datetime(trimestre, errors="coerce")

    if "result_df" in st.session_state:
        df_form = st.session_state["result_df"].copy()
    else:
        st.error("Veuillez d'abord importer et calculer les données dans 'Importation & Calculs'.")
        st.stop()
    # ====== OUTILS COMMUNS (à définir 1 seule fois) ======

    def normalize_bu(bu):
        if isinstance(bu, str):
            return bu.strip().upper().replace("É", "E")
        return bu

    bu_mapping = {
        "ALLEMAGNE": "ALLEMAGNE",
        "APAC - CHINE": "APAC CHINE",
        "ESPAGNE": "ESPAGNE",
        "EUROPE DU NORD": "EUROPE DU NORD",
        "FRANCE": "FRANCE",
        "FRANCE_TÉLÉVENTE": "FRANCE",
        "FRANCE WEISS": "FRANCE",
        "FRANCE  KAM GAM": "FRANCE",
        "France KAM GAM": "FRANCE",
        "ITALIE": "ITALIE",
        "JAPON": "JAPON",
        "RETAIL INTERNATIONAL": "RETAIL",
        "CORPORATE GIFTING": "RETAIL",
        "MAISONS": "ALL",
        "USA - CANADA": "USA CANADA"
    }
    bu_mapping_norm = {normalize_bu(k): normalize_bu(v) for k, v in bu_mapping.items()}

    def get_participants_par_bu(df_participants: pd.DataFrame) -> pd.DataFrame:
        """Retourne un DF: BU_clean | Nb Participants (uniques Nom+Prénom)"""
        dfp = df_participants.copy()
        dfp["BU_clean"] = dfp["Groupes"].apply(normalize_bu).replace(bu_mapping_norm)
        dfp["Nom"] = dfp["Nom"].astype(str).str.strip().str.upper()
        dfp["Prénom"] = dfp["Prénom"].astype(str).str.strip().str.upper()

        dfp_unique = dfp.drop_duplicates(subset=["BU_clean", "Nom", "Prénom"])

        out = dfp_unique["BU_clean"].value_counts().reset_index()
        out.columns = ["BU_clean", "Nb Participants"]
        return out
    
    df_participants = None
    if "calendar_file" in st.session_state:
        try:
            df_participants = pd.read_excel(
                st.session_state["calendar_file"],
                sheet_name="BDD Participants 2026",
                header=2
            )
        except Exception:
            df_participants = None
    df_ta = pd.read_excel(st.session_state["calendar_file"], sheet_name="TA 2026")

    df_form["BU"] = df_form["BU"].astype(str).str.strip()
    df_form["Population"] = df_form["Population"].astype(str).str.lower().str.strip()

    df_ta.columns = df_ta.iloc[0]
    df_ta = df_ta[1:]
    df_ta["Type de TA"] = df_ta["Type de TA"].astype(str).str.lower().str.strip()
    df_ta["BU"] = df_ta["Groupe"].astype(str).str.strip()
    df_ta["Formateur"] = df_ta["Formateur"].astype(str).str.strip().str.lower()
    # Conversion des dates
    df_form["Date de début"] = df_form["Date de début"].apply(convert_trimestre_to_date)
    df_ta.rename(columns={"Date": "Date de début"}, inplace=True)
    df_ta["Date de début"] = df_ta["Date de début"].apply(convert_trimestre_to_date)

    # Dates min/max globales
    min_date = min(df_form["Date de début"].min(), df_ta["Date de début"].min())
    max_date = max(df_form["Date de début"].max(), df_ta["Date de début"].max())

    df_ta["Nb jours"] = pd.to_numeric(df_ta["Nb jours"], errors="coerce").fillna(0)

    form_count = df_form.groupby(["BU", "Population"]).agg({
        "Module": "count",
        "Nb participant": lambda x: pd.to_numeric(x, errors="coerce").sum(),
        "CA": lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum(),
        "Cout formateur": lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum()
    }).reset_index().rename(columns={
        "Module": "Nb Formations",
        "Nb participant": "Nb Participants",
        "CA": "Budget (Formation)",
        "Cout formateur": "Réel (Formation)"
    })

    def get_formateur_cost(name):
        return pu_data.get(name.lower().strip(), 600)

    df_ta["Coût unitaire"] = df_ta["Formateur"].map(get_formateur_cost)
    df_ta["CA réalisé"] = df_ta["Nb jours"] * df_ta["Coût unitaire"]

    ta_count = df_ta.groupby(["BU", "Type de TA"]).agg({
        "Participant": "count",
        "Nb jours": "sum",
        "CA réalisé": "sum"
    }).reset_index().rename(columns={
        "Participant": "Nb TA",
        "Nb jours": "Nb jours TA",
        "CA réalisé": "Coût (Réel)"
    })

    ta_count["CA"] = ta_count["Type de TA"].map(ta_budget_data).fillna(0) * ta_count["Nb TA"]

    ta_pivot = ta_count.pivot(index="BU", columns="Type de TA", values="Nb TA").fillna(0)
    ta_budget = ta_count.groupby("BU")[["CA", "Coût (Réel)"]].sum().reset_index()

    merged = form_count.groupby("BU").agg({
        "Nb Formations": "sum",
        "Nb Participants": "sum",
        "Budget (Formation)": "sum",
        "Réel (Formation)": "sum"
    }).reset_index()

    merged = merged.merge(ta_budget, on="BU", how="left").fillna(0)
    merged = merged.merge(ta_pivot, on="BU", how="left").fillna(0)

    merged["Budget Total"] = merged["Budget (Formation)"] + merged["CA"]
    merged["Réel Total"] = merged["Réel (Formation)"] + merged["Coût (Réel)"]

    # st.subheader("🧾 Vue consolidée par BU")
    # st.dataframe(merged.style.format({
    #     "Budget (Formation)": "{:,.2f} €",
    #     "Réel (Formation)": "{:,.2f} €",
    #     "CA": "{:,.2f} €",
    #     "Coût (Réel)": "{:,.2f} €",
    #     "Budget Total": "{:,.2f} €",
    #     "Réel Total": "{:,.2f} €"
    # }))

    # CSS personnalisé pour les onglets st.tabs
    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #F3F4F6;
            border-radius: 4px 4px 0px 0px;
            padding: 8px 16px;
            color: #4B5563;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E3A8A !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialisation des onglets
    tab1, tab2, tab3 = st.tabs(["📘 Formations par BU", "📙 TA par BU", "📉 Rentabilité WSA"])

    def blue_row_style(row):
        return ['background-color: rgba(0, 51, 160, 0.3)' for _ in row]

    with tab1: 
        def parse_euro_series(s: pd.Series) -> pd.Series:
            """Convertit une série '1,234.56 €' en float 1234.56"""
            return pd.to_numeric(
                s.astype(str)
                .str.replace("€", "", regex=False)
                .str.replace("\u202f", "", regex=False)   # espace fine insécable
                .str.replace("\xa0", "", regex=False)     # espace insécable
                .str.replace(" ", "", regex=False)
                .str.replace(",", "", regex=False),       # retire séparateur milliers
                errors="coerce"
            ).fillna(0)

        def count_participants_from_bdd(df_participants: pd.DataFrame, population_filter: str | None = None) -> int:
            """
            Compte les participants DISTINCTS depuis 'BDD Participants 2026'.
            - Unicité: Email si dispo, sinon Nom+Prénom
            - Filtre sur colonne 'Population' si population_filter est fourni
            """
            dfp = df_participants.copy()

            dfp["Population"] = dfp["Population"].astype(str).str.strip().str.lower()
            dfp["Email"] = dfp["Email"].astype(str).str.strip().str.lower()
            dfp["Nom"] = dfp["Nom"].astype(str).str.strip().str.upper()
            dfp["Prénom"] = dfp["Prénom"].astype(str).str.strip().str.upper()

            # ID participant: Email si présent, sinon Nom+Prénom
            dfp["participant_id"] = np.where(
                dfp["Email"].notna() & (dfp["Email"] != "") & (dfp["Email"] != "nan"),
                dfp["Email"],
                dfp["Nom"] + "|" + dfp["Prénom"]
            )

            if population_filter and population_filter.lower().strip() != "toute population":
                pop = population_filter.lower().strip()
                dfp = dfp[dfp["Population"] == pop]

            return int(dfp["participant_id"].nunique())

        
            # ----------- 🔹 Bloc 1 : Formations seules -----------
            #                 # --- KPIs ---
            # Sauvegarder une version non filtrée pour les KPI globaux
        df_form_original = df_form.copy()  # sauvegarde complète pour les totaux
            # Widgets de filtre de date
        date_range = st.date_input(
            "📅 Filtrer par Date de début et fin",
            value=[min_date, max_date],
            key="date_range_bu"
        )

        # 🛡️ Sécurité : l'utilisateur doit choisir une période complète
        if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
            st.sidebar.info("ℹ️ Merci de sélectionner une **date de fin** pour appliquer le filtre.")
            st.stop()

        start_date, end_date = date_range


        # ✅ Base intacte (ne pas toucher df_form directement)
        df_form_base = df_form_original.copy()

        # ✅ 1) Filtre date d'abord (toutes BU)
        df_form_date = df_form_base[
            (df_form_base["Date de début"] >= pd.Timestamp(start_date)) &
            (df_form_base["Date de début"] <= pd.Timestamp(end_date))
        ].copy()

        # ✅ 2) Liste BU dépendante de la période
        bu_form_list = sorted(df_form_date["BU"].dropna().unique())

        # ✅ 3) Multiselect BU (par défaut = toutes les BU de la période)
        selected_bu_form = st.multiselect(
            "Filtrer les Formations par BU",
            options=bu_form_list,
            default=bu_form_list,
            key=f"form_bu_filter_{start_date}_{end_date}"
)


        # ✅ 4) Appliquer BU sur les données déjà filtrées date
        df_form = df_form_date[df_form_date["BU"].isin(selected_bu_form)].copy()

        # ✅ Référence globale (toutes BU) = uniquement date
        df_form_ref = df_form_date.copy()

        # (optionnel) total global (si tu veux garder un KPI global)
        nb_formations_global = df_form_base["Module"].count()



        df_ta = df_ta[
            (df_ta["Date de début"] >= pd.Timestamp(start_date)) &
            (df_ta["Date de début"] <= pd.Timestamp(end_date))
        ]

        # ➤ Calcul après filtre
        nb_formations_filtrées = df_form["Module"].count()

        # ✅ KPI Nb formations (dynamique car df_form est déjà filtré BU + dates)
        # ✅ Réalisées dans la BU filtrée
        nb_realisees_filtre = df_form[df_form["Maintenue / Annulée"] == "Réalisée"]["Module"].count()

        # ✅ Réalisées globales (toutes BU) mais sur la même période (df_form_ref)
        nb_realisees_total = df_form_base[df_form_base["Maintenue / Annulée"].isin(["Réalisée","Maintenue"])]["Module"].count()




        pourcentage_formations = (nb_realisees_filtre / nb_realisees_total) * 100 if nb_realisees_total != 0 else 0



        st.subheader("Indicateurs Clés")
        st.markdown("""
        <style>
        .card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px;
        }
        .card h2 {
            font-size: 2rem;
            margin: 0;
        }
        .card p {
            margin: 5px 0;
            font-size: 1.2rem;
            color: #333;
        }
        .card .green {
            color: green;
            font-size: 0.9rem;
            margin-top: 5px;
        }
                        .delta {
        font-size: 1.2rem;
        margin-top: 5px;
        }
        .label {
            font-size: 1rem;
            color: #555;
        }
        .positive {
            color: green;
        }
        .negative {
            color: red;
        }
        </style>
        """, unsafe_allow_html=True)
        
        ventilation_form = df_form.groupby(["BU"]).agg({
            "Module": "count",
            "Nb participant": lambda x: pd.to_numeric(x, errors="coerce").sum(),
            "CA": lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum(),
            "Cout formateur": lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum()
        }).reset_index().rename(columns={
            "Module": "Nb Formations",
            "Nb participant": "Nb Participants",
            "CA": "CA",
            "Cout formateur": "Coût (Réel)"
        })
        # Exclure la ligne "Total" si déjà concaténée
        df_kpi = ventilation_form[ventilation_form["BU"] != "Total"]
        # Calcul des totaux AVANT ajout de la ligne Total
        total_ca = ventilation_form["CA"].sum()
        total_reel = ventilation_form["Coût (Réel)"].sum()
        total_formations = ventilation_form["Nb Formations"].sum()
        percentage_budget_used = (total_reel / total_ca) * 100 if total_ca != 0 else 0
        # Solde restant et %
        solde_restant = total_ca - total_reel
        percentage_budget_remaining = (solde_restant / total_ca ) * 100 if total_ca  != 0 else 0
        # pourcentage_formations = (nb_formations_filtrées / nb_formations_global) * 100 if nb_formations_global != 0 else 0
        df_form["Maintenue / Annulée"] = df_form["Maintenue / Annulée"].astype(str).str.strip()
        df_form_ref["Maintenue / Annulée"] = df_form_ref["Maintenue / Annulée"].astype(str).str.strip()
        df_form_base["Maintenue / Annulée"] = df_form_base["Maintenue / Annulée"].astype(str).str.strip()


        def get_delta_class(delta):
            return "positive" if delta >= 0 else "negative"
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="card">
                <h2>{total_ca:,.2f} €</h2>
                <p>Total CA réalisé</p>
                <div class="delta positive">100%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <h2>{total_reel:,.2f} €</h2>
                <p>Total Coût Formateur </p>
                <div class="delta {get_delta_class(percentage_budget_used)}">{percentage_budget_used:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="card">
                <h2>{solde_restant:,.2f} €</h2>
                <p>Rentabilité</p>
                <div class="delta {get_delta_class(percentage_budget_remaining)}">{percentage_budget_remaining:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="card">
                <h2>{nb_realisees_filtre} / {nb_realisees_total}</h2>
                <p>Nb de Formations (Réalisées)</p>
                <div class="delta positive">{pourcentage_formations:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)


        # with col5:
        #     if df_participants is None or "Population" not in df_participants.columns:
        #         st.warning("⚠️ Impossible de lire 'BDD Participants 2026' → fallback sur Nb participant du calendrier.")
        #         populations = df_form["Population"].dropna().unique()
        #         selected_population = st.selectbox("Filtrer par population", options=["Toute population"] + list(populations))

        #         df_filtered = df_form if selected_population == "Toute population" else df_form[df_form["Population"] == selected_population]

        #         nb_part = pd.to_numeric(df_filtered["Nb participant"], errors="coerce").sum()
        #         cout_total = parse_euro_series(df_filtered["Cout formateur"]).sum()
        #         cout_moyen_filtered = cout_total / nb_part if nb_part != 0 else 0

        #     else:
        #         # ✅ Populations depuis la base participants (source de vérité)
        #         pop_list = (
        #             df_participants["Population"]
        #             .dropna()
        #             .astype(str).str.strip().str.lower()
        #             .unique()
        #         )
        #         pop_list = sorted([p for p in pop_list if p and p != "nan"])

        #         selected_population = st.selectbox(
        #             "Filtrer par population",
        #             options=["Toute population"] + pop_list
        #         )

        #         # ➕ Filtrer les coûts côté formations sur la même population
        #         df_filtered = df_form if selected_population == "Toute population" else df_form[df_form["Population"] == selected_population]

        #         cout_total = parse_euro_series(df_filtered["Cout formateur"]).sum()

        #         # ✅ Denominateur = nb participants DISTINCTS depuis BDD Participants 2026
        #         nb_participants_bdd = count_participants_from_bdd(df_participants, selected_population)

        #         cout_moyen_filtered = cout_total / nb_participants_bdd if nb_participants_bdd != 0 else 0

        #     st.markdown(f"""
        #     <div class="card">
        #         <h2>{cout_moyen_filtered:,.2f} €</h2>
        #         <p>Coût moyen / participant</p>
        #     </div>
        #     """, unsafe_allow_html=True)


        # --- Ventilation Formations par BU (avec Nb Participants corrigé via df_participants) ---

        # 1) Base ventilation (Formations / CA / Coût)
        ventilation_form = (
            df_form.assign(BU_clean=df_form["BU"].apply(normalize_bu))
            .groupby("BU_clean")
            .agg(
                **{
                    "Nb Formations": ("Module", "count"),
                    "CA": ("CA", lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum()),
                    "Coût Formateur": ("Cout formateur", lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum()),
                }
            )
            .reset_index()
        )

        # # 2) Ajouter Nb Participants si df_participants dispo
        # if df_participants is not None:
        #     participants_par_bu = get_participants_par_bu(df_participants)  # BU_clean | Nb Participants
        #     ventilation_form = ventilation_form.merge(participants_par_bu, on="BU_clean", how="left")
        #     ventilation_form["Nb Participants"] = ventilation_form["Nb Participants"].fillna(0).astype(int)
        # else:
        #     ventilation_form["Nb Participants"] = 0

        # 3) Renommer BU_clean -> BU pour affichage
        ventilation_form = ventilation_form.rename(columns={"BU_clean": "BU"})
        ventilation_form = ventilation_form[["BU", "Nb Formations", "CA", "Coût Formateur"]]

        st.subheader("Ventilation Formations par BU")
        # ➕ Ligne de total
        total_form = pd.DataFrame({
            "BU": ["Total"],
            "Nb Formations": [ventilation_form["Nb Formations"].sum()],
            # "Nb Participants": [ventilation_form["Nb Participants"].sum()],
            "CA": [ventilation_form["CA"].sum()],
            "Coût Formateur": [ventilation_form["Coût Formateur"].sum()]
        })

        ventilation_form = pd.concat([ventilation_form, total_form], ignore_index=True)
        # ➕ Calculs des colonnes supplémentaires
        ventilation_form["Rentabilité"] = ventilation_form["CA"] - ventilation_form["Coût Formateur"]

        ventilation_form["% Rentabilité"] = ventilation_form.apply(
            lambda row: (row["Rentabilité"] / row["CA"]) * 100 if row["CA"] != 0 else 0,
            axis=1
        )
        # ventilation_form["Coût moyen par participant"] = ventilation_form.apply(
        #     lambda row: row["Coût Formateur"] / row["Nb Participants"] if row["Nb Participants"] > 0 else 0,
        #     axis=1
        # )

        styled_ventilation_form = (
            ventilation_form.style
            .apply(blue_row_style, axis=1)   # ✅ couleur sur chaque ligne
            .format({
                "CA": "{:,.2f} €",
                "Coût Formateur": "{:,.2f} €",
                "Rentabilité": "{:,.2f} €",
                "% Rentabilité": "{:.0f} %",
                "Nb Formations": "{:.0f}",
                # "Nb Participants": "{:.0f}",
                "Coût moyen par participant": "{:,.2f} €"
            })
        )

        st.dataframe(styled_ventilation_form, use_container_width=True, hide_index=True)

        # Préparation des colonnes
        ventilation_form["Rentabilité"] = ventilation_form["CA"] - ventilation_form["Coût Formateur"]

        # Créer un DataFrame "long" pour barres groupées
        df_bar = ventilation_form[ventilation_form["BU"] != "Total"][["BU", "CA", "Coût Formateur", "Rentabilité"]]
        df_bar_long = df_bar.melt(id_vars="BU", var_name="Type", value_name="Montant (€)")

        st.subheader("Comparatif [ CA / Coût Formateur / Rentabilité par BU ]")
        fig = px.bar(
            df_bar_long,
            x="BU",
            y="Montant (€)",
            color="Type",
            barmode="group",
            text_auto=".2s",
            color_discrete_map={
                "CA": "#0033A0",       # Bleu
                "Coût (Réel)": "#FF6666",       # Rouge clair
                "Rentabilité": "#4CAF50"      # Vert
            }
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        # 🔹 Courbe Évolution CA & Coût cumulé par mois (Formations)
        df_monthly_form = df_form.copy()
        df_monthly_form["Mois"] = df_monthly_form["Date de début"].dt.to_period("M").dt.to_timestamp()

        # Nettoyage numérique
        df_monthly_form["CA"] = pd.to_numeric(df_monthly_form["CA"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").fillna(0)
        df_monthly_form["Cout formateur"] = pd.to_numeric(df_monthly_form["Cout formateur"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").fillna(0)

        df_grouped_form = df_monthly_form.groupby("Mois")[["CA", "Cout formateur"]].sum().sort_index().cumsum().reset_index()
        df_grouped_form = df_grouped_form.rename(columns={"CA": "CA Cumulé", "Cout formateur": "Cout formateur Cumulé"})

        df_form_long = df_grouped_form.melt(id_vars="Mois", var_name="Type", value_name="Montant (€)")

        st.subheader("📈 Évolution CA vs Coût formateur cumulé (Formations)")
        fig_form = px.line(
            df_form_long,
            x="Mois",
            y="Montant (€)",
            color="Type",
            markers=True,
            text="Montant (€)",
            color_discrete_map={
                "Cout formateur Cumulé": "#66B2FF",
                "CA Cumulé": "#0033A0"
            }
        )
        fig_form.update_traces(texttemplate="%{text:,.0f} €", textposition="top right")
        fig_form.update_layout(yaxis_title="Montant (€)", xaxis_title="Mois")
        st.plotly_chart(fig_form, use_container_width=True)

        

        
        

    with tab2:
        # ----------- 🔹 Bloc 2 : TA seules ----------

        # 1. Sauvegarder la version non filtrée pour KPI global
        df_ta_original = df_ta.copy()
        # 1) garder une base intacte
        df_ta_base = df_ta_original.copy()

        # 2) toujours convertir la date sur la base (IMPORTANT)
        df_ta_base["Date de début"] = df_ta_base["Date de début"].apply(convert_trimestre_to_date)

        # 3) filtre date
        date_range = st.date_input(
            "📅 Filtrer par Date de début et fin",
            value=[min_date, max_date],
            key="date_range_bu_taa"
        )

        # 🛡️ Sécurité : l'utilisateur doit choisir une période complète
        if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
            st.sidebar.info("ℹ️ Merci de sélectionner une **date de fin** pour appliquer le filtre.")
            st.stop()

        start_date, end_date = date_range


        df_ta_date = df_ta_base[
            (df_ta_base["Date de début"] >= pd.Timestamp(start_date)) &
            (df_ta_base["Date de début"] <= pd.Timestamp(end_date))
        ].copy()

        # 4) liste BU dépendante de la période
        bu_ta_list = sorted(df_ta_date["BU"].dropna().unique())

        # 5) multiselect BU (par défaut = toutes les BU de la période)
        selected_bu_ta = st.multiselect(
            "Filtrer les TA par BU",
            options=bu_ta_list,
            default=bu_ta_list,
            key="ta_bu_filter"
        )

        # 6) appliquer BU sur les données déjà filtrées date
        df_ta = df_ta_date[df_ta_date["BU"].isin(selected_bu_ta)].copy()



        # 3. Calcul global vs filtré
        nb_ta_global = df_ta_original.shape[0]
        nb_ta_filtrées = df_ta.shape[0]
        pourcentage_ta = (nb_ta_filtrées / nb_ta_global) * 100 if nb_ta_global != 0 else 0

        # Recalculer le ta_count à partir du df_ta filtré
        ta_count_filtered = df_ta.groupby(["BU", "Type de TA"]).agg({
            "Participant": "count",
            "Nb jours": "sum",
            "CA réalisé": "sum"
        }).reset_index().rename(columns={
            "Participant": "Nb TA",
            "Nb jours": "Nb jours TA",
            "CA réalisé": "Coût Formateur"
        })

        ta_count_filtered["CA"] = ta_count_filtered["Type de TA"].map(ta_budget_data).fillna(0) * ta_count_filtered["Nb TA"]

        # Ventilation par BU
        ventilation_ta = ta_count_filtered.groupby("BU")[["CA", "Coût Formateur"]].sum().reset_index()

        # TA par type
        obs_ta = ta_count_filtered[ta_count_filtered["Type de TA"] == "observation"].set_index("BU")["Nb TA"]
        suivi_ta = ta_count_filtered[ta_count_filtered["Type de TA"] == "suivi & contrôle"].set_index("BU")["Nb TA"]

        # Fusionner les deux colonnes
        ventilation_ta["Nb TA Observation"] = ventilation_ta["BU"].map(obs_ta).fillna(0).astype(int)
        ventilation_ta["Nb TA Suivi"] = ventilation_ta["BU"].map(suivi_ta).fillna(0).astype(int)

        # Réorganiser
        ventilation_ta = ventilation_ta[["BU", "Nb TA Observation", "Nb TA Suivi", "CA", "Coût Formateur"]]

        st.subheader("Indicateurs Clés")

        # Nettoyage : retirer ligne Total si déjà concaténée
        df_kpi_ta = ventilation_ta[ventilation_ta["BU"] != "Total"]

        # Calculs principaux
        total_ca_ta = df_kpi_ta["CA"].sum()
        total_reel_ta = df_kpi_ta["Coût Formateur"].sum()
        total_ta_obs = df_kpi_ta["Nb TA Observation"].sum()
        total_ta_suivi = df_kpi_ta["Nb TA Suivi"].sum()
        total_ta = total_ta_obs + total_ta_suivi

        # Pourcentages
        percentage_used_ta = (total_reel_ta / total_ca_ta * 100) if total_ca_ta != 0 else 0
        solde_ta = total_ca_ta - total_reel_ta
        percentage_remaining_ta = (solde_ta / total_ca_ta * 100) if total_ca_ta != 0 else 0

        def get_delta_class(delta):
            return "positive" if delta >= 0 else "negative"

        # Affichage sous forme de cartes
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="card">
                <h2>{total_ca_ta:,.2f} €</h2>
                <p>Total CA réalisé</p>
                <div class="delta positive">100%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <h2>{total_reel_ta:,.2f} €</h2>
                <p>Total Coût Formateur</p>
                <div class="delta {get_delta_class(percentage_used_ta)}">{percentage_used_ta:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="card">
                <h2>{solde_ta:,.2f} €</h2>
                <p>Rentabilité</p>
                <div class="delta {get_delta_class(percentage_remaining_ta)}">{percentage_remaining_ta:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="card">
                <h2>{nb_ta_filtrées} / {nb_ta_global}</h2>
                <p>Nb Total de TA (Réalisées)</p>
                <div class="delta positive">{pourcentage_ta:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        st.subheader(" Ventilation TA par BU")
        # ➕ Ligne de total
        total_ta = pd.DataFrame({
            "BU": ["Total"],
            "Nb TA Observation": [ventilation_ta["Nb TA Observation"].sum()],
            "Nb TA Suivi": [ventilation_ta["Nb TA Suivi"].sum()],
            "CA": [ventilation_ta["CA"].sum()],
            "Coût Formateur": [ventilation_ta["Coût Formateur"].sum()]
        })

        ventilation_ta = pd.concat([ventilation_ta, total_ta], ignore_index=True)

        # Ajouter colonne Maintenu (à réaliser) = Budget - Réel
        ventilation_ta["Rentabilité"] = ventilation_ta["CA"] - ventilation_ta["Coût Formateur"]

        # Ajouter % Écart = Maintenu / Budget
        ventilation_ta["% Rentabilité"] = ventilation_ta.apply(
            lambda row: (row["Rentabilité"] / row["CA"]) * 100 if row["CA"] != 0 else 0,
            axis=1
        )

        # ✅ style bleu + format €
        st.dataframe(
            ventilation_ta.style
                .apply(blue_row_style, axis=1)
                .format({
                    "CA": "{:,.2f} €",
                    "Coût Formateur": "{:,.2f} €",
                    "Rentabilité": "{:,.2f} €",
                    "% Rentabilité": "{:.0f} %",
                    "Nb TA Observation": "{:.0f}",
                    "Nb TA Suivi": "{:.0f}",
                }),
            use_container_width=True, 
            hide_index=True
        )

        # ➕ Préparer les colonnes
        ventilation_ta["Rentabilité"] = ventilation_ta["CA"] - ventilation_ta["Coût Formateur"]

        # ➕ Graphique : Barres groupées pour Budget, Réel et Solde
        df_bar_ta = ventilation_ta[ventilation_ta["BU"] != "Total"][["BU", "CA", "Coût Formateur", "Rentabilité"]]
        df_bar_ta_long = df_bar_ta.melt(id_vars="BU", var_name="Type", value_name="Montant (€)")

        st.subheader("Comparatif TA [ CA / Coût Formateur / Rentabilité par BU ]")
        fig_ta = px.bar(
            df_bar_ta_long,
            x="BU",
            y="Montant (€)",
            color="Type",
            barmode="group",
            text_auto=".2s",
            color_discrete_map={
                "CA": "#0033A0",       # Bleu
                "Coût Formateur": "#FF6666",       # Rouge clair
                "Rentabilité": "#4CAF50"      # Vert
            }
        )
        fig_ta.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_ta, use_container_width=True)
        # 🔹 Courbe Évolution CA & Coût cumulé par mois (TA)
        df_monthly_ta = df_ta.copy()
        df_monthly_ta["Mois"] = df_monthly_ta["Date de début"].dt.to_period("M").dt.to_timestamp()

        df_monthly_ta["CA"] = df_monthly_ta["Type de TA"].map(ta_budget_data).fillna(0)
        df_monthly_ta["Coût Formateur"] = df_monthly_ta["Nb jours"] * df_monthly_ta["Coût unitaire"]

        df_grouped_ta = df_monthly_ta.groupby("Mois")[["CA", "Coût Formateur"]].sum().sort_index().cumsum().reset_index()
        df_grouped_ta = df_grouped_ta.rename(columns={"CA": "CA Cumulé", "Coût Formateur": "Coût Formateur Cumulé"})

        df_ta_long = df_grouped_ta.melt(id_vars="Mois", var_name="Type", value_name="Montant (€)")

        st.subheader("📈 Évolution CA vs Coût formateur cumulé (TA)")
        fig_ta = px.line(
            df_ta_long,
            x="Mois",
            y="Montant (€)",
            color="Type",
            markers=True,
            text="Montant (€)",
            color_discrete_map={
                "Coût Formateur Cumulé": "#66B2FF",
                "CA Cumulé": "#0033A0"
            }
        )
        fig_ta.update_traces(texttemplate="%{text:,.0f} €", textposition="top right")
        fig_ta.update_layout(yaxis_title="Montant (€)", xaxis_title="Mois")
        st.plotly_chart(fig_ta, use_container_width=True)

    with tab3:
                # --- Mise en forme avec couleurs personnalisées
        def highlight_type(row):
            color = ""
            if row["Type"] == "TA":
                color = "background-color: #FFCC80;"  # orange clair
            elif row["Type"] == "Formation":
                color = "background-color: #64B5F6;"  # bleu clair
            elif row["Type"] == "Ingénierie":
                color = "background-color: #E8F5E9;"  # vert très pâle
            elif row["Type"] == "TOTAL":
                color = "background-color: #BDBDBD;"  # gris clair
            return [color] * len(row)
        
        def normalize_bu(bu):
            if isinstance(bu, str):
                return bu.strip().upper().replace("É", "E")  # Pour éviter accents
            return bu

        df_form["BU"] = df_form["BU"].apply(normalize_bu)
        df_ta["BU"] = df_ta["BU"].apply(normalize_bu)

        # st.subheader("Ventilation Budgets T1 par BU")

        # # --- INPUT modifiable : Budget total Ingénierie ---
        # budget_t1_inge = st.number_input("💼 Budget T1 - Ingénierie (modifiable)", value=101000, step=1000)
        budget_t1_inge = 101000  # valeur fixe, sans affichage UI

        # 1. Harmoniser les noms de BU (majuscule standardisée)
        df_form["BU_clean"] = df_form["BU"].str.upper().str.strip()
        df_ta["BU_clean"] = df_ta["BU"].str.upper().str.strip()

        # 2. Recalculer les budgets groupés sur BU_clean
        formation_budget = (
            df_form.groupby("BU_clean")["CA"]
            .apply(lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum())
            .to_dict()
        )

        # Ajouter colonne BU_clean
        df_ta["BU_clean"] = df_ta["BU"].str.upper().str.strip()

        # Calcul du CA TA si pas déjà présent
        df_ta["CA"] = df_ta["Type de TA"].map(ta_budget_data).fillna(0)

        # Groupement propre avec nom de BU nettoyé
        ta_budget = (
            df_ta.groupby("BU_clean")["CA"]
            .sum()
            .to_dict()
        )


        # 3. Liste finale des BU normalisées (triée)
        bu_list = sorted(set(formation_budget.keys()) | set(ta_budget.keys()))

        # --- Répartition proportionnelle de l’ingénierie ---
        # Option 1 : répartition égale (tu peux la rendre dynamique plus tard)
        n_bu = len(bu_list)
        inge_per_bu = {bu: budget_t1_inge / n_bu for bu in bu_list}

        # --- Construction du tableau final ---
        data = {
            "Type": ["Ingénierie", "TA", "Formation", "TOTAL"]
        }

        for bu in bu_list:
            data[bu] = [
                "-",  # tiret pour Ingénierie
                ta_budget.get(bu, 0),
                formation_budget.get(bu, 0),
                ta_budget.get(bu, 0) + formation_budget.get(bu, 0)
            ]


        df_budget = pd.DataFrame(data)
        df_budget.loc[df_budget["Type"] == "Ingénierie", "TOTAL"] = budget_t1_inge

        # Calcul manuel du total sauf pour la ligne "Ingénierie"
        df_budget["TOTAL"] = df_budget.apply(
            lambda row: budget_t1_inge if row["Type"] == "Ingénierie"
            else sum(x for x in row[bu_list] if isinstance(x, (int, float))),
            axis=1
        )
            # Ajouter budget ingénierie total à la ligne "TOTAL" colonne "TOTAL"
        df_budget.loc[df_budget["Type"] == "TOTAL", "TOTAL"] = (
            df_budget.loc[df_budget["Type"] == "TOTAL", "TOTAL"].values[0] + budget_t1_inge
        )


        # --- Conversion des colonnes numériques uniquement (évite Type qui est str)
        cols_to_format = df_budget.columns.difference(['Type'])
        df_budget[cols_to_format] = df_budget[cols_to_format].apply(pd.to_numeric, errors='coerce')

        styled_budget = df_budget.style \
            .format(lambda x: f"{x:,.0f} €" if isinstance(x, (int, float)) else x, subset=cols_to_format) \
            .apply(highlight_type, axis=1)



        # # --- Affichage
        # st.dataframe(styled_budget)
        
        # col1,col2=st.columns([1,2])
        # with col1:
        # st.subheader("Rentabilité par Formateur")
        # Nettoyage des données
        df_form["Cout formateur"] = pd.to_numeric(df_form["Cout formateur"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce")
        df_form["CA"] = pd.to_numeric(df_form["CA"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce")
        df_form["Formateur 1"] = df_form["Formateur 1"].astype(str).str.strip().str.title()

        df_ta["Formateur"] = df_ta["Formateur"].astype(str).str.strip().str.title()
        df_ta["Nb jours"] = pd.to_numeric(df_ta["Nb jours"], errors="coerce").fillna(0)
        df_ta["Coût unitaire"] = df_ta["Formateur"].map(get_formateur_cost)
        df_ta["Coût (TA)"] = df_ta["Nb jours"] * df_ta["Coût unitaire"]
        df_ta["CA"] = df_ta["Type de TA"].map(ta_budget_data).fillna(0)

        # Coût par formateur
        cout_form = df_form.groupby("Formateur 1")["Cout formateur"].sum()
        cout_ta = df_ta.groupby("Formateur")["Coût (TA)"].sum()

        # Index formateurs fusionné
        all_formateurs = sorted(set(cout_form.index) | set(cout_ta.index))
        df_renta = pd.DataFrame(index=all_formateurs)
        df_renta["Formation + Prépa WSA"] = cout_form
        df_renta["TA"] = cout_ta
        df_renta["Total (€)"] = df_renta[["Formation + Prépa WSA", "TA"]].sum(axis=1)

        # Ligne TOTAL
        total_row = pd.DataFrame(df_renta.sum(numeric_only=True)).T
        total_row.index = ["TOTAL"]
        df_renta = pd.concat([df_renta, total_row])

        # # Format premier tableau
        # df_renta_display = df_renta.fillna("")
        # cols_to_format = ["Formation + Prépa WSA", "TA", "Total (€)"]
        # for col in cols_to_format:
        #     df_renta_display[col] = df_renta_display[col].apply(lambda x: f"{x:,.0f} €" if isinstance(x, (int, float)) else x)

        # # Fonction de coloration par colonne (application correcte)
        # def highlight_columns(df):
        #     styles = pd.DataFrame("", index=df.index, columns=df.columns)
        #     styles["Formation + Prépa WSA"] = "background-color: #64B5F6"  # Bleu
        #     styles["TA"] = "background-color: #FFA726"  # Orange
        #     styles["Total (€)"] = "background-color: #BDBDBD"  # Gris
        #     return styles

        # df_renta_display_styled = df_renta_display.style.apply(highlight_columns, axis=None)

        # st.dataframe(df_renta_display_styled)

        # with col2: 
        st.subheader("Détails Rentabilité par BU")

        # Nettoyage des valeurs monétaires
        for col in ["CA", "Cout formateur"]:
            df_form[col] = pd.to_numeric(df_form[col].astype(str).str.replace("\u20ac", "").str.replace(",", ""), errors="coerce")
        df_ta["Coût (TA)"] = pd.to_numeric(df_ta["Coût (TA)"], errors="coerce")

        # Regrouper les coûts réels par BU
        cout_form_bu = (
            df_form.groupby("BU_clean")["Cout formateur"]
            .sum()
            .reset_index()
            .rename(columns={"Cout formateur": "Coût Formateur"})
        )

        cout_ta_bu = (
            df_ta.groupby("BU_clean")["Coût (TA)"]
            .sum()
            .reset_index()
            .rename(columns={"Coût (TA)": "Coût TA"})
        )

        # Calcul du CA (budget) par BU
        ca_form_bu = (
            df_form.groupby("BU_clean")["CA"]
            .sum()
            .reset_index()
            .rename(columns={"CA": "CA Formateur"})
        )

        df_ta["CA"] = df_ta["Type de TA"].map(ta_budget_data).fillna(0)
        ca_ta_bu = (
            df_ta.groupby("BU_clean")["CA"]
            .sum()
            .reset_index()
            .rename(columns={"CA": "CA TA"})
        )

        # Fusion des données
        renta_bu = ca_form_bu.merge(cout_form_bu, on="BU_clean", how="outer")
        renta_bu = renta_bu.merge(ca_ta_bu, on="BU_clean", how="outer")
        renta_bu = renta_bu.merge(cout_ta_bu, on="BU_clean", how="outer").fillna(0)

        # Calculs de rentabilité
        renta_bu["Rentabilité Form."] = renta_bu["CA Formateur"] - renta_bu["Coût Formateur"]
        renta_bu["Rentabilité TA"] = renta_bu["CA TA"] - renta_bu["Coût TA"]
        renta_bu["Rentabilité Totale"] = renta_bu["Rentabilité Form."] + renta_bu["Rentabilité TA"]

        # Formatage affichage
        cols_to_format = ["CA Formateur", "Coût Formateur", "Rentabilité Form.", "CA TA", "Coût TA", "Rentabilité TA", "Rentabilité Totale"]
        for col in cols_to_format:
            renta_bu[col] = renta_bu[col].apply(lambda x: f"{x:,.0f} €")

        st.dataframe(renta_bu, hide_index=True)
        st.subheader("Synthèse Rentabilité Globale")
        def highlight_columns_resume(df):
            styles = pd.DataFrame("", index=df.index, columns=df.columns)
            styles["Formation + Prépa WSA"] = "background-color: #64B5F6"
            styles["Tournée accompagnée"] = "background-color: #FFA726"
            styles["Total (€)"] = "background-color: #BDBDBD"
            return styles

        # Données CA
        ca_form = df_form["CA"].sum()
        df_ta["CA"] = df_ta["Type de TA"].map(ta_budget_data).fillna(0)
        ca_ta = df_ta["CA"].sum()
        ca_total = ca_form + ca_ta

        # Coûts déjà récupérés depuis df_renta ligne "TOTAL"
        cout_form_total = df_renta.loc["TOTAL", "Formation + Prépa WSA"]
        cout_ta_total = df_renta.loc["TOTAL", "TA"]
        cout_total = df_renta.loc["TOTAL", "Total (€)"]

        # Rentabilité
        rentabilite = ca_total - cout_total
        pourcent = (rentabilite / ca_total * 100) if ca_total != 0 else 0

        # Tableau de synthèse
        df_resume = pd.DataFrame({
            "Formation + Prépa WSA": [ca_form, cout_form_total, ca_form - cout_form_total, (ca_form - cout_form_total)/ca_form*100 if ca_form else 0],
            "Tournée accompagnée": [ca_ta, cout_ta_total, ca_ta - cout_ta_total, (ca_ta - cout_ta_total)/ca_ta*100 if ca_ta else 0],
            "Total (€)": [ca_total, cout_total, rentabilite, pourcent]
        }, index=["CA", "TOTAL (Coût Formateur)", "Rentabilité (€)", "% Rentabilité"])
        # ➕ Réordonner les lignes pour afficher TOTAL en premier
        df_resume = df_resume.loc[["TOTAL (Coût Formateur)", "CA", "Rentabilité (€)", "% Rentabilité"]]
        # Formatage final
        def format_euro_or_percent(val, row_name):
            if isinstance(val, (int, float)):
                if row_name == "% Rentabilité":
                    return f"{val:.1f} %"
                else:
                    return f"{val:,.0f} €"
            return val

        for col in df_resume.columns:
            df_resume[col] = df_resume.apply(lambda row: format_euro_or_percent(row[col], row.name), axis=1)
        df_resume_styled = df_resume.style
        for col in df_resume.columns:
            df_resume_styled = df_resume_styled.applymap(lambda v: highlight_columns_resume(v, col), subset=[col])

        df_resume_styled = df_resume.style.apply(highlight_columns_resume, axis=None)
        st.dataframe(df_resume_styled, hide_index=True)
        col1,col2 = st.columns(2)
        with col1: 
            labels = ["Formation + Prépa WSA", "Tournée accompagnée"]
            values = [cout_form_total, cout_ta_total]

            fig_pie = go.Figure(
                data=[go.Pie(
                    labels=labels, 
                    values=values, 
                    hole=0.4,  # Donut chart pour esthétique
                    textinfo='label+percent+value'
                )]
            )
            fig_pie.update_layout(title="Répartition globale des Coûts")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2: 
            st.subheader("Visualisation Rentabilité")

            # Ajouter un expander avec un choix de graphe
            with st.expander("Sélectionner la visualisation",True):
                choix_graph = st.radio("Choisir un graphique :", ["Par Formateur", "Par BU"])
                if choix_graph == "Par Formateur":
                    # On retire la ligne TOTAL pour le graphique
                    df_renta_graph = df_renta.drop("TOTAL")
                    df_renta_graph["Rentabilité (€)"] = df_renta_graph["Total (€)"].astype(float)

                    # On reset l’index pour avoir une colonne "Formateur"
                    df_renta_graph_reset = df_renta_graph.reset_index()
                    df_renta_graph_reset.rename(columns={'index': 'Formateur'}, inplace=True)

                    # Barplot
                    fig_renta = px.bar(
                        df_renta_graph_reset,
                        x="Formateur",
                        y="Rentabilité (€)",
                        color="Rentabilité (€)",
                        color_continuous_scale="Blues",
                        labels={"Formateur": "Formateur", "Rentabilité (€)": "Rentabilité (€)"},
                        title="Rentabilité par Formateur"
                    )
                    fig_renta.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_renta, use_container_width=True)

                elif choix_graph == "Par BU":
                    # Nettoyage BU pour être homogène (tu l'as déjà fait normalement)
                    df_form["BU_clean"] = df_form["BU"].str.upper().str.strip()
                    df_ta["BU_clean"] = df_ta["BU"].str.upper().str.strip()

                    # Coût formation par BU
                    cout_form_bu = (
                        df_form.groupby("BU_clean")["Cout formateur"]
                        .sum()
                        .reset_index()
                        .rename(columns={"Cout formateur": "Coût Formation"})
                    )

                    # Coût TA par BU
                    cout_ta_bu = (
                        df_ta.groupby("BU_clean")["Coût (TA)"]
                        .sum()
                        .reset_index()
                        .rename(columns={"Coût (TA)": "Coût TA"})
                    )

                    # Fusion des deux
                    df_cout_bu = pd.merge(cout_form_bu, cout_ta_bu, on="BU_clean", how="outer").fillna(0)
                    # Convertir les dictionnaires en dataframe
                    df_budget_form = pd.DataFrame.from_dict(formation_budget, orient="index", columns=["CA Formation"]).reset_index().rename(columns={"index": "BU_clean"})
                    df_budget_ta = pd.DataFrame.from_dict(ta_budget, orient="index", columns=["CA TA"]).reset_index().rename(columns={"index": "BU_clean"})

                    # Fusionner
                    df_budget_bu = pd.merge(df_budget_form, df_budget_ta, on="BU_clean", how="outer").fillna(0)
                    df_bu = pd.merge(df_cout_bu, df_budget_bu, on="BU_clean", how="outer").fillna(0)

                    # Calcul rentabilité
                    df_bu["Rentabilité Formation"] = df_bu["CA Formation"] - df_bu["Coût Formation"]
                    df_bu["Rentabilité TA"] = df_bu["CA TA"] - df_bu["Coût TA"]


                    # Préparer les données au bon format (long form pour plotly)
                    df_bu_melt = df_bu.melt(
                        id_vars="BU_clean",
                        value_vars=["Rentabilité Formation", "Rentabilité TA"],
                        var_name="Type",
                        value_name="Rentabilité (€)"
                    )

                    fig_bu = px.bar(
                        df_bu_melt,
                        x="BU_clean",
                        y="Rentabilité (€)",
                        color="Type",
                        color_discrete_map={
                            "Rentabilité Formation": "#4F81BD",  # Bleu formation
                            "Rentabilité TA": "#6BAED6"          # Bleu plus clair pour TA
                        },
                        title="Rentabilité par BU (Formation & Tournée accompagnée)",
                        labels={"BU_clean": "BU", "Rentabilité (€)": "Rentabilité (€)"}
                    )
                    fig_bu.update_layout(xaxis_tickangle=-45)

                    st.plotly_chart(fig_bu, use_container_width=True)



        # st.subheader("📉 Rentabilité par Formateur")

        # # Nettoyer les colonnes de coût et CA dans df_form et df_ta
        # df_form["Cout formateur"] = pd.to_numeric(df_form["Cout formateur"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").fillna(0)
        # df_form["CA"] = pd.to_numeric(df_form["CA"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").fillna(0)

        # df_ta["Coût unitaire"] = df_ta["Formateur"].map(get_formateur_cost)
        # df_ta["Nb jours"] = pd.to_numeric(df_ta["Nb jours"], errors="coerce").fillna(0)
        # df_ta["Coût formateur"] = df_ta["Nb jours"] * df_ta["Coût unitaire"]
        # df_ta["CA"] = df_ta["Type de TA"].map(ta_budget_data).fillna(0)

        # # Agrégation par formateur
        # df_formateurs_form = df_form.groupby("Formateur 1").agg({
        #     "CA": "sum",
        #     "Cout formateur": "sum"
        # }).reset_index().rename(columns={
        #     "Formateur 1": "Formateur",
        #     "CA": "CA Formation",
        #     "Cout formateur": "Coût Formation"
        # })

        # df_formateurs_ta = df_ta.groupby("Formateur").agg({
        #     "CA": "sum",
        #     "Coût formateur": "sum"
        # }).reset_index().rename(columns={
        #     "CA": "CA TA",
        #     "Coût formateur": "Coût TA"
        # })

        # # Fusion des deux
        # rentabilite = pd.merge(df_formateurs_form, df_formateurs_ta, on="Formateur", how="outer").fillna(0)

        # # Total et Rentabilité
        # rentabilite["CA Total"] = rentabilite["CA Formation"] + rentabilite["CA TA"]
        # rentabilite["Coût Total"] = rentabilite["Coût Formation"] + rentabilite["Coût TA"]
        # rentabilite["Rentabilité (€)"] = rentabilite["CA Total"] - rentabilite["Coût Total"]

        # # Formatage final
        # st.dataframe(
        #     rentabilite.style.format({
        #         "CA Formation": "{:,.0f} €",
        #         "CA TA": "{:,.0f} €",
        #         "CA Total": "{:,.0f} €",
        #         "Coût Formation": "{:,.0f} €",
        #         "Coût TA": "{:,.0f} €",
        #         "Coût Total": "{:,.0f} €",
        #         "Rentabilité (€)": "{:,.0f} €"
        #     })
        # )

elif selected =="RAPPORT CLIENT":
    st.title("Rapport Client - Ventilation par BU")
    # Fonction de conversion des trimestres et de "Février"
    def convert_trimestre_to_date(trimestre):
        if isinstance(trimestre, str):
            trimestre = trimestre.strip().lower()
            if trimestre == "trimestre 1":
                return pd.Timestamp("2026-01-01")
            elif trimestre == "trimestre 2":
                return pd.Timestamp("2026-04-01")
            elif trimestre == "trimestre 3":
                return pd.Timestamp("2026-07-01")
            elif trimestre == "février":
                return pd.Timestamp("2026-02-01")
            elif trimestre == "tbc":
                return pd.Timestamp("2026-12-31")
            elif trimestre == "tbc in sept-oct":
                return pd.Timestamp("2026-09-01")
            elif trimestre == "tbc (octobre)":
                return pd.Timestamp("2026-10-01")
            elif trimestre == "tbc (novembre)":         
                return pd.Timestamp("2026-11-01")
        return pd.to_datetime(trimestre, errors="coerce")
    
    def format_montant(x):
        if pd.isnull(x):
            return ""
        return f"{x:,.2f}".replace(",", " ").replace(".", ",") + " €"

    if "result_df" in st.session_state:
        df_form = st.session_state["result_df"].copy()
    else:
        st.error("Veuillez d'abord importer et calculer les données dans 'Importation & Calculs'.")
        st.stop()

    df_ta = pd.read_excel(st.session_state["calendar_file"], sheet_name="TA 2026")

    # ===== Participants (pour Nb Participants corrigé) =====
    df_participants = None
    try:
        df_participants = pd.read_excel(
            st.session_state["calendar_file"],
            sheet_name="BDD Participants 2026",
            header=2
        )
    except Exception:
        df_participants = None

    def normalize_bu(bu):
        if isinstance(bu, str):
            return bu.strip().upper().replace("É", "E")
        return bu

    bu_mapping = {
        "ALLEMAGNE": "ALLEMAGNE",
        "APAC - CHINE": "APAC CHINE",
        "ESPAGNE": "ESPAGNE",
        "EUROPE DU NORD": "EUROPE DU NORD",
        "FRANCE": "FRANCE",
        "FRANCE_TÉLÉVENTE": "FRANCE",
        "FRANCE WEISS": "FRANCE",
        "FRANCE  KAM GAM": "FRANCE",
        "FRANCE KAM GAM": "FRANCE",
        "ITALIE": "ITALIE",
        "JAPON": "JAPON",
        "RETAIL INTERNATIONAL": "RETAIL",
        "CORPORATE GIFTING": "RETAIL",
        "MAISONS": "ALL",
        "USA - CANADA": "USA CANADA"
    }
    bu_mapping_norm = {normalize_bu(k): normalize_bu(v) for k, v in bu_mapping.items()}

    def get_participants_par_bu(df_participants: pd.DataFrame) -> pd.DataFrame:
        dfp = df_participants.copy()
        dfp["BU_clean"] = dfp["Groupes"].apply(normalize_bu).replace(bu_mapping_norm)
        dfp["Nom"] = dfp["Nom"].astype(str).str.strip().str.upper()
        dfp["Prénom"] = dfp["Prénom"].astype(str).str.strip().str.upper()

        # Unicité : BU + Nom + Prénom
        dfp_unique = dfp.drop_duplicates(subset=["BU_clean", "Nom", "Prénom"])

        out = dfp_unique["BU_clean"].value_counts().reset_index()
        out.columns = ["BU_clean", "Nb Participants"]
        return out
    
# ===========================================================
    #  Nb participants reliés via la colonne "Groupes"
    #  (Formations 2026  ↔  BDD Participants 2026)
    # ===========================================================
    def _norm_groupe(s):
        return str(s).strip().upper() if pd.notnull(s) else s

    def get_nb_participants_par_bu_via_groupes(df_form, df_participants):
        """Nb de participants DISTINCTS (Nom+Prénom) par BU.
        Lien : 'Groupes' de Formations 2026  ↔  'Groupes' de BDD Participants 2026.
        Retourne un dict { BU_normalisée : nb_participants }."""
        if df_participants is None:
            return {}
        f = df_form.copy()
        p = df_participants.copy()
        f["__grp"] = f["Groupes"].apply(_norm_groupe)
        f["__bu"]  = f["BU"].apply(normalize_bu)
        p["__grp"] = p["Groupes"].apply(_norm_groupe)
        p["__nom"] = p["Nom"].astype(str).str.strip().str.upper()
        p["__pre"] = p["Prénom"].astype(str).str.strip().str.upper()

        bu_to_groupes = (
            f.dropna(subset=["__bu"])
             .groupby("__bu")["__grp"]
             .apply(lambda s: set(g for g in s if pd.notnull(g)))
        )
        out = {}
        for bu, groupes in bu_to_groupes.items():
            sub = p[p["__grp"].isin(groupes)]
            out[bu] = int(sub.drop_duplicates(subset=["__nom", "__pre"]).shape[0])
        return out

    def get_nb_participants_distinct_total_via_groupes(df_form, df_participants):
        """Nb de participants DISTINCTS au global (toutes BU affichées),
        SANS double comptage des groupes partagés (ex : FRANCE)."""
        if df_participants is None:
            return 0
        f = df_form.copy()
        p = df_participants.copy()
        groupes = set(g for g in f["Groupes"].apply(_norm_groupe) if pd.notnull(g))
        p["__grp"] = p["Groupes"].apply(_norm_groupe)
        p["__nom"] = p["Nom"].astype(str).str.strip().str.upper()
        p["__pre"] = p["Prénom"].astype(str).str.strip().str.upper()
        sub = p[p["__grp"].isin(groupes)]
        return int(sub.drop_duplicates(subset=["__nom", "__pre"]).shape[0])
    
    def get_nb_participants_par_groupe(df_participants, groupes_autorises=None):
            """Nb de participants DISTINCTS (Nom+Prénom) par Groupe (BDD Participants 2026).
            groupes_autorises : itérable de groupes normalisés à conserver (sinon tous)."""
            if df_participants is None:
                return {}
            p = df_participants.copy()
            p["__grp"] = p["Groupes"].apply(_norm_groupe)
            p["__nom"] = p["Nom"].astype(str).str.strip().str.upper()
            p["__pre"] = p["Prénom"].astype(str).str.strip().str.upper()
            p = p.dropna(subset=["__grp"])
            if groupes_autorises is not None:
                p = p[p["__grp"].isin(set(groupes_autorises))]
            return p.drop_duplicates(subset=["__grp", "__nom", "__pre"]).groupby("__grp").size().to_dict()

    def get_ventilation_formations_par_groupe(df_form, df_participants):
        """Ventilation des formations par Groupes (colonne 'Groupes' de Formations 2026)."""
        f = df_form.copy()
        f["__grp"] = f["Groupes"].apply(_norm_groupe)
        f = f[f["__grp"].notna()]
        f["__ca"] = pd.to_numeric(
            f["CA"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce"
        ).fillna(0)
        f["__statut"] = f["Maintenue / Annulée"].astype(str).str.lower().str.strip()

        base = f.groupby("__grp").agg(
            **{"Nb Formations": ("Module", "count"), "CA": ("__ca", "sum")}
        ).reset_index()
        realise = (
            f[f["__statut"] == "réalisée"].groupby("__grp")["__ca"].sum()
            .reset_index().rename(columns={"__ca": "CA Réalisé"})
        )
        out = base.merge(realise, on="__grp", how="left")
        out["CA Réalisé"] = out["CA Réalisé"].fillna(0)

        nb = get_nb_participants_par_groupe(df_participants, out["__grp"].tolist())
        out["Nb Participants"] = out["__grp"].map(nb).fillna(0).astype(int)

        out = out.rename(columns={"__grp": "Groupes"})
        return out[["Groupes", "Nb Formations", "Nb Participants", "CA", "CA Réalisé"]]
   
    df_form["BU"] = df_form["BU"].astype(str).str.strip()
    df_form["Population"] = df_form["Population"].astype(str).str.lower().str.strip()

    df_ta.columns = df_ta.iloc[0]
    df_ta = df_ta[1:]
    df_ta["Type de TA"] = df_ta["Type de TA"].astype(str).str.lower().str.strip()
    df_ta["BU"] = df_ta["Groupe"].astype(str).str.strip()
    df_ta["Formateur"] = df_ta["Formateur"].astype(str).str.strip().str.lower()
    # Conversion des dates
    df_form["Date de début"] = df_form["Date de début"].apply(convert_trimestre_to_date)
    df_ta.rename(columns={"Date": "Date de début"}, inplace=True)
    df_ta["Date de début"] = df_ta["Date de début"].apply(convert_trimestre_to_date)

    # Dates min/max globales
    min_date = min(df_form["Date de début"].min(), df_ta["Date de début"].min())
    max_date = max(df_form["Date de début"].max(), df_ta["Date de début"].max())

    df_ta["Nb jours"] = pd.to_numeric(df_ta["Nb jours"], errors="coerce").fillna(0)

    form_count = df_form.groupby(["BU", "Population"]).agg({
        "Module": "count",
        "Nb participant": lambda x: pd.to_numeric(x, errors="coerce").sum(),
        "CA": lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum(),
        "Cout formateur": lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum()
    }).reset_index().rename(columns={
        "Module": "Nb Formations",
        "Nb participant": "Nb Participants",
        "CA": "Budget (Formation)",
        "Cout formateur": "Réel (Formation)"
    })

    def get_formateur_cost(name):
        return pu_data.get(name.lower().strip(), 600)

    df_ta["Coût unitaire"] = df_ta["Formateur"].map(get_formateur_cost)
    df_ta["CA réalisé"] = df_ta["Nb jours"] * df_ta["Coût unitaire"]

    ta_count = df_ta.groupby(["BU", "Type de TA"]).agg({
        "Participant": "count",
        "Nb jours": "sum",
        "CA réalisé": "sum"
    }).reset_index().rename(columns={
        "Participant": "Nb TA",
        "Nb jours": "Nb jours TA",
        "CA réalisé": "Coût (Réel)"
    })

    ta_count["CA"] = ta_count["Type de TA"].map(ta_budget_data).fillna(0) * ta_count["Nb TA"]

    ta_pivot = ta_count.pivot(index="BU", columns="Type de TA", values="Nb TA").fillna(0)
    ta_budget = ta_count.groupby("BU")[["CA", "Coût (Réel)"]].sum().reset_index()

    merged = form_count.groupby("BU").agg({
        "Nb Formations": "sum",
        "Nb Participants": "sum",
        "Budget (Formation)": "sum",
        "Réel (Formation)": "sum"
    }).reset_index()

    merged = merged.merge(ta_budget, on="BU", how="left").fillna(0)
    merged = merged.merge(ta_pivot, on="BU", how="left").fillna(0)

    merged["Budget Total"] = merged["Budget (Formation)"] + merged["CA"]
    merged["Réel Total"] = merged["Réel (Formation)"] + merged["Coût (Réel)"]

    # st.subheader("🧾 Vue consolidée par BU")
    # st.dataframe(merged.style.format({
    #     "Budget (Formation)": "{:,.2f} €",
    #     "Réel (Formation)": "{:,.2f} €",
    #     "CA": "{:,.2f} €",
    #     "Coût (Réel)": "{:,.2f} €",
    #     "Budget Total": "{:,.2f} €",
    #     "Réel Total": "{:,.2f} €"
    # }))

    # CSS personnalisé pour les onglets st.tabs
    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #F3F4F6;
            border-radius: 4px 4px 0px 0px;
            padding: 8px 16px;
            color: #4B5563;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E3A8A !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialisation des onglets
    # tab1, tab2, tab3, tab4 = st.tabs(["📘 Formations WSA", "📙 TA WSA ", "⚙️ Ingénierie WSA","📊 Ventilation Budgets"])
    tab1, tab2, tab3 = st.tabs(["📘 Formations WSA", "📙 TA WSA ","📊 Ventilation Budgets"])
    # 🎨 Fonction pour colorer les lignes en bleu très clair
    def blue_row_style(row):
        return ['background-color: rgba(0, 51, 160, 0.3)' for _ in row]

    # 🔴 Fonction pour colorer en rouge les zéros dans les colonnes concernées
    def highlight_zeros(val):
        if isinstance(val, (int, float)) and val == 0:
            return 'color: #ff4d4d; font-weight: bold;'
        return ''
    
    with tab1: 
            # ----------- 🔹 Bloc 1 : Formations seules -----------
            #                 # --- KPIs ---
            # Sauvegarder une version non filtrée pour les KPI globaux
        df_form_original = df_form.copy()  # sauvegarde complète pour les totaux
        df_form["Maintenue / Annulée"] = df_form["Maintenue / Annulée"].astype(str).str.strip().str.capitalize()

            # Widgets de filtre de date
        date_range = st.date_input(
            "📅 Filtrer par Date de début et fin",
            value=[min_date, max_date],
            key="date_range_bu"
        )

        # 🛡️ Sécurité : l'utilisateur doit choisir une période complète
        if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
            st.sidebar.info("ℹ️ Merci de sélectionner une **date de fin** pour appliquer le filtre.")
            st.stop()

        start_date, end_date = date_range


        # Déclaration du filtre BU
        # ✅ 1) Filtrer d'abord par date (sur une base intacte)
        df_form_date = df_form_original[
            (df_form_original["Date de début"] >= pd.Timestamp(start_date)) &
            (df_form_original["Date de début"] <= pd.Timestamp(end_date))
        ].copy()

        # ✅ 2) Liste BU uniquement dans la période
        bu_form_list = sorted(df_form_date["BU"].dropna().unique())

        # ✅ 3) Multiselect BU (par défaut : toutes les BU de la période)
        selected_bu_form = st.multiselect(
            "Filtrer les Formations par BU",
            options=bu_form_list,
            default=bu_form_list,
            key=f"form_bu_filter_{start_date}_{end_date}"
        )
# ✅ 3 bis) Filtre par Groupe + par Zone (colonnes "Groupes" et "ZONE" de Formations 2026)
        df_form_date["Groupes"] = df_form_date["Groupes"].astype(str).str.strip()
        df_form_date["ZONE"]    = df_form_date["ZONE"].astype(str).str.strip()

        groupe_form_list = sorted(g for g in df_form_date["Groupes"].dropna().unique() if g and g != "nan")
        selected_groupe_form = st.multiselect(
            "Filtrer les Formations par Groupe",
            options=groupe_form_list,
            default=groupe_form_list,
            key=f"form_groupe_filter_{start_date}_{end_date}"
        )

        zone_form_list = sorted(z for z in df_form_date["ZONE"].dropna().unique() if z and z != "nan")
        selected_zone_form = st.multiselect(
            "Filtrer les Formations par Zone",
            options=zone_form_list,
            default=zone_form_list,
            key=f"form_zone_filter_{start_date}_{end_date}"
        )
        # =========================
        # ✅ 4) Filtre Statut (appliqué SUR df_form_date)
        # =========================
        df_form_date["Maintenue / Annulée"] = df_form_date["Maintenue / Annulée"].astype(str).str.strip().str.capitalize()

        maintenue_list = sorted(df_form_date["Maintenue / Annulée"].dropna().unique().tolist(), key=lambda x: x.lower().strip())

        st.sidebar.subheader("📘 Filtrage des Formations")
        selected_maintenue = st.sidebar.multiselect(
            "Filtrer les Formations par Statut (Maintenue / Annulée)",
            options=maintenue_list,
            default=maintenue_list,
            key="maintenue_filter_form"
        )

        # ✅ df_form = données finales filtrées : Date + BU + Statut
        df_form = df_form_date[
                    (df_form_date["BU"].isin(selected_bu_form)) &
                    (df_form_date["Groupes"].isin(selected_groupe_form)) &
                    (df_form_date["ZONE"].isin(selected_zone_form)) &
                    (df_form_date["Maintenue / Annulée"].isin(selected_maintenue))
                ].copy()

        # =========================
        # ✅ KPI "Réalisées / Totales" (dans le contexte filtré)
        # =========================
        nb_formations_total = df_form["Module"].count()

        df_realisees = df_form[df_form["Maintenue / Annulée"].str.lower().str.strip() == "réalisée"].copy()
        nb_formations_realisees = df_realisees["Module"].count()
        # =========================
        # ✅ CA (Budget) et CA Réalisé
        # =========================

        # Nettoyage CA sur df_form_original (pour budget)
        df_form_original["CA"] = pd.to_numeric(
            df_form_original["CA"].astype(str).str.replace("€", "").str.replace(",", ""),
            errors="coerce"
        ).fillna(0)

        # Nettoyage CA sur df_realisees (pour réalisé)
        df_realisees["CA"] = pd.to_numeric(
            df_realisees["CA"].astype(str).str.replace("€", "").str.replace(",", ""),
            errors="coerce"
        ).fillna(0)

        # ✅ Budget = sans filtre date, MAIS avec filtre BU (comme tu faisais avant)
        df_form_budget = df_form_original[df_form_original["BU"].isin(selected_bu_form)].copy()
        total_ca = df_form_budget["CA"].sum()

        # ✅ Réalisé = uniquement les "réalisées" dans le contexte filtré (date + BU + statut)
        total_ca_realise = df_realisees["CA"].sum()

        # Solde et %
        solde_restant = total_ca - total_ca_realise
        percentage_budget_remaining = (solde_restant / total_ca) * 100 if total_ca != 0 else 0

        pourcentage_formations = (nb_formations_realisees / nb_formations_total) * 100 if nb_formations_total != 0 else 0



        st.subheader("Indicateurs Clés")
        st.markdown("""
        <style>
        .card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin: 10px;
        }
        .card h2 {
            font-size: 2rem;
            margin: 0;
        }
        .card p {
            margin: 5px 0;
            font-size: 1.2rem;
            color: #333;
        }
        .card .green {
            color: green;
            font-size: 0.9rem;
            margin-top: 5px;
        }
                        .delta {
        font-size: 1.2rem;
        margin-top: 5px;
        }
        .label {
            font-size: 1rem;
            color: #555;
        }
        .positive {
            color: green;
        }
        .negative {
            color: red;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Budget par BU (sans filtre de date, avec filtre BU)
        df_budget_bu = df_form_budget.groupby("BU").agg({
            "CA": "sum"
        }).reset_index().rename(columns={"CA": "CA"})

        # Indicateurs filtrés (avec filtre de date)
        df_indics_bu = df_form.groupby("BU").agg({
            "Module": "count",
            "Nb participant": lambda x: pd.to_numeric(x, errors="coerce").sum(),
            "Cout formateur": lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum()
        }).reset_index().rename(columns={
            "Module": "Nb Formations",
            "Nb participant": "Nb Participants",
            "Cout formateur": "Coût (Réel)"
        })
        # ➕ Ajout de la colonne "CA" nettoyée pour traitement
        df_form["CA"] = pd.to_numeric(
            df_form["CA"].astype(str).str.replace("€", "").str.replace(",", ""),
            errors="coerce"
        ).fillna(0)

        # ➕ Formations réalisées uniquement (filtrées date + BU déjà appliqué)
        df_form_real = df_form[df_form["Maintenue / Annulée"].str.lower().str.strip() == "réalisée"].copy()

        # ➕ Total CA Réalisé par BU
        df_realise_bu = df_form_real.groupby("BU").agg({
            "CA": "sum"
        }).reset_index().rename(columns={"CA": "CA Réalisé"})

        # ✅ Fusion finale des indicateurs
        ventilation_form = df_indics_bu \
            .merge(df_budget_bu, on="BU", how="left") \
            .merge(df_realise_bu, on="BU", how="left") \
            .fillna(0)

        # Fusion des deux sources
        ventilation_form = pd.merge(df_indics_bu, df_budget_bu, on="BU", how="left").fillna(0)

        # Exclure la ligne "Total" si déjà concaténée
        df_kpi = ventilation_form[ventilation_form["BU"] != "Total"]
        total_formations = ventilation_form["Nb Formations"].sum()
        # Solde restant et %
        solde_restant = total_ca - total_ca_realise
        percentage_budget_remaining = (solde_restant / total_ca ) * 100 if total_ca  != 0 else 0


        def get_delta_class(delta):
            return "positive" if delta >= 0 else "negative"
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="card">
                <h2>{format_montant(total_ca)}</h2>
                <p>Total CA</p>
                <div class="delta positive">100%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            pourcentage_realise = (total_ca_realise / total_ca) * 100 if total_ca != 0 else 0
            st.markdown(f"""
            <div class="card">
                <h2>{format_montant(total_ca_realise)}</h2>
                <p>Total CA Réalisé</p>
                <div class="delta {get_delta_class(pourcentage_realise)}">{pourcentage_realise:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="card">
                <h2>{format_montant(solde_restant)}</h2>
                <p>Solde Restant</p>
                <div class="delta {get_delta_class(percentage_budget_remaining)}">{percentage_budget_remaining:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="card">
                <h2>{nb_formations_realisees} / {nb_formations_total}</h2>
                <p>Nb de Formations (Réalisées / Totales)</p>
                <div class="delta positive">{pourcentage_formations:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)


        # ===== Ventilation Formations par BU (Nb Participants corrigé via df_participants) =====

        # 1) Budget par BU (filtré BU uniquement, pas de date)
        df_budget_bu = df_form_budget.groupby("BU").agg({"CA": "sum"}).reset_index().rename(columns={"CA": "CA"})

        # 2) CA Réalisé par BU (avec date + BU + Réalisées)
        df_realise_bu = df_realisees.groupby("BU").agg({"CA": "sum"}).reset_index().rename(columns={"CA": "CA Réalisé"})

        # 3) Nb Formations (depuis df_form filtré date+BU)
        df_indics_bu = df_form.groupby("BU").agg({
            "Module": "count"
        }).reset_index().rename(columns={"Module": "Nb Formations"})

        # # 4) Nb Participants corrigé depuis la feuille Participants (sur la même BU filtrée)
        # # 4) Nb Participants : reliés via la colonne "Groupes" (Formations 2026 ↔ BDD Participants 2026)
        # if df_participants is not None:
        #     nb_part_par_bu = get_nb_participants_par_bu_via_groupes(df_form, df_participants)
        #     df_indics_bu["Nb Participants"] = (
        #         df_indics_bu["BU"].apply(normalize_bu).map(nb_part_par_bu).fillna(0).astype(int)
        #     )
        # else:
        #     df_indics_bu["Nb Participants"] = 0

        # 5) Fusion finale
        ventilation_form = df_indics_bu \
            .merge(df_budget_bu, on="BU", how="left") \
            .merge(df_realise_bu, on="BU", how="left") \
            .fillna(0)


        st.subheader("Ventilation Formations par BU")
        # ➕ Ligne de total
        total_form = pd.DataFrame({
            "BU": ["Total"],
            "Nb Formations": [ventilation_form["Nb Formations"].sum()],
            # "Nb Participants": [get_nb_participants_distinct_total_via_groupes(df_form, df_participants)],
            "CA": [ventilation_form["CA"].sum()],
            "CA Réalisé": [ventilation_form["CA Réalisé"].sum()]
        })

        ventilation_form = pd.concat([ventilation_form, total_form], ignore_index=True)
        # ➕ Calculs des colonnes supplémentaires
        ventilation_form["Maintenu (à réaliser)"] = ventilation_form["CA"] - ventilation_form["CA Réalisé"]

        ventilation_form["% Ecart"] = ventilation_form.apply(
            lambda row: (row["Maintenu (à réaliser)"] / row["CA"]) * 100 if row["CA"] != 0 else 0,
            axis=1
        )
        # ventilation_form["Coût moyen par participant"] = ventilation_form.apply(
        #     lambda row: row["CA Réalisé"] / row["Nb Participants"] if row["Nb Participants"] > 0 else 0,
        #     axis=1
        # )

        styled_ventilation_form = ventilation_form.style.format({
            "CA": "{:,.2f} €",
            "CA Réalisé": "{:,.2f} €",
            "Maintenu (à réaliser)": "{:,.2f} €",
            "% Ecart": "{:.0f} %",
            "Nb Formations": "{:.0f}",
            # "Nb Participants": "{:.0f}"
            # "Coût moyen par participant": "{:,.2f} €"
        }).apply(blue_row_style, axis=1).applymap(highlight_zeros, subset=["CA Réalisé", "Maintenu (à réaliser)", "% Ecart"])

        st.dataframe(styled_ventilation_form, hide_index=True)
        # ===== Ventilation Formations par GROUPES =====
        st.subheader("Ventilation Formations par Groupes")
        ventilation_grp = get_ventilation_formations_par_groupe(df_form, df_participants)

        total_grp = pd.DataFrame({
            "Groupes": ["Total"],
            "Nb Formations": [ventilation_grp["Nb Formations"].sum()],
            "Nb Participants": [get_nb_participants_distinct_total_via_groupes(df_form, df_participants)],
            "CA": [ventilation_grp["CA"].sum()],
            "CA Réalisé": [ventilation_grp["CA Réalisé"].sum()],
        })
        ventilation_grp = pd.concat([ventilation_grp, total_grp], ignore_index=True)

        ventilation_grp["Maintenu (à réaliser)"] = ventilation_grp["CA"] - ventilation_grp["CA Réalisé"]
        ventilation_grp["% Ecart"] = ventilation_grp.apply(
            lambda r: (r["Maintenu (à réaliser)"] / r["CA"]) * 100 if r["CA"] != 0 else 0, axis=1
        )

        styled_grp = ventilation_grp.style.format({
            "CA": "{:,.2f} €", "CA Réalisé": "{:,.2f} €", "Maintenu (à réaliser)": "{:,.2f} €",
            "% Ecart": "{:.0f} %", "Nb Formations": "{:.0f}", "Nb Participants": "{:.0f}",
        }).apply(blue_row_style, axis=1).applymap(highlight_zeros, subset=["CA Réalisé", "Maintenu (à réaliser)", "% Ecart"])

        st.dataframe(styled_grp, hide_index=True)
        # Préparation des colonnes
        ventilation_form["Solde Restant"] = ventilation_form["CA"] - ventilation_form["CA Réalisé"]
        # ➕ Tableau des formations réalisées
        st.subheader("📋 Détail des Formations Réalisées")

        # Colonnes à afficher
        colonnes_a_afficher = [
            "BU", "Module", "Population", "CA réalisé", "Date de début"
        ]


        # Nettoyage de la colonne CA
        df_form_real["CA"] = pd.to_numeric(
            df_form_real["CA"].astype(str).str.replace("€", "").str.replace(",", ""),
            errors="coerce"
        ).fillna(0)

        # Renommer la colonne pour l'affichage
        df_form_real = df_form_real.rename(columns={"CA": "CA réalisé"})

        # Affichage du tableau
        df_form_display = df_form_real[colonnes_a_afficher].sort_values("Date de début", ascending=False)

        styled_form = df_form_display.style.format({
            "CA réalisé": "{:,.2f} €"
        }).apply(blue_row_style, axis=1).applymap(highlight_zeros, subset=["CA réalisé"])

        st.dataframe(styled_form, hide_index=True)


        # Créer un DataFrame "long" pour barres groupées
        df_bar = ventilation_form[ventilation_form["BU"] != "Total"][["BU", "CA", "CA Réalisé", "Solde Restant"]]
        df_bar_long = df_bar.melt(id_vars="BU", var_name="Type", value_name="Montant (€)")

        st.subheader("Comparatif CA / CA réalisé / Maintenu à réaliser par BU")
        fig = px.bar(
            df_bar_long,
            x="BU",
            y="Montant (€)",
            color="Type",
            barmode="group",
            text_auto=".2s",
            color_discrete_map={
                "CA": "#0033A0",       # Bleu
                "CA Réalisé": "#66B2FF",       # Rouge clair
                "Solde Restant": "#66BB66"       # Vert
            }
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # 🔹 Courbe Évolution CA & Réel cumulé par mois (Formations)
        df_monthly_form = df_form.copy()
        df_monthly_form["Mois"] = df_monthly_form["Date de début"].dt.to_period("M").dt.to_timestamp()

        # Nettoyage numérique
        df_monthly_form["CA"] = pd.to_numeric(df_monthly_form["CA"].astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").fillna(0)

        # ➤ Formations Réalisées uniquement pour la courbe réelle
        df_monthly_realise = df_monthly_form[df_monthly_form["Maintenue / Annulée"].str.lower().str.strip() == "réalisée"]

        # ➕ Groupe 1 : Budget cumulé (toutes les formations visibles)
        df_budget_group = df_monthly_form.groupby("Mois")[["CA"]].sum().cumsum().rename(columns={"CA": "CA Cumulé"})

        # ➕ Groupe 2 : Réel cumulé (seulement "réalisées")
        df_real_group = df_monthly_realise.groupby("Mois")[["CA"]].sum().cumsum().rename(columns={"CA": "CA réalisé Cumulé"})

        # ➕ Fusion des deux courbes
        df_grouped_form = pd.concat([df_budget_group, df_real_group], axis=1).fillna(method="ffill").fillna(0).reset_index()

        # ➕ Long format
        df_form_long = df_grouped_form.melt(id_vars="Mois", var_name="Type", value_name="Montant (€)")

        # 📈 Plotly Line Chart
        st.subheader("📈 Évolution CA vs CA réalisé (Formations)")
        fig_form = px.line(
            df_form_long,
            x="Mois",
            y="Montant (€)",
            color="Type",
            markers=True,
            text="Montant (€)",
            color_discrete_map={
                "CA Cumulé": "#0033A0",
                "CA réalisé Cumulé": "#66B2FF"
            }
        )
        fig_form.update_traces(texttemplate="%{text:,.0f} €", textposition="top right")
        fig_form.update_layout(yaxis_title="Montant (€)", xaxis_title="Mois")
        st.plotly_chart(fig_form, use_container_width=True)


        

        
        

    with tab2:
        def format_montant(x):
            if pd.isnull(x):
                return ""
            return f"{x:,.2f}".replace(",", " ").replace(".", ",") + " €"        
        from datetime import date
        aujourd_hui = pd.to_datetime(date.today())
        # 1. Sauvegarder la version non filtrée pour KPI global
        df_ta_original = df_ta.copy()
        # Widgets de filtre de date
        date_range = st.date_input(
            "📅 Filtrer par Date de début et fin",
            value=[min_date, max_date],
            key="date_range_bu_ta"
        )

        # 🛡️ Sécurité : l'utilisateur doit choisir une période complète
        if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
            st.sidebar.info("ℹ️ Merci de sélectionner une **date de fin** pour appliquer le filtre.")
            st.stop()

        start_date, end_date = date_range

        # ✅ 1) Filtrer d'abord par date (base intacte)
        df_ta_original["Date de début"] = df_ta_original["Date de début"].apply(convert_trimestre_to_date)

        df_ta_date = df_ta_original[
            (df_ta_original["Date de début"] >= pd.Timestamp(start_date)) &
            (df_ta_original["Date de début"] <= pd.Timestamp(end_date))
        ].copy()

        # ✅ 2) Liste BU uniquement dans la période
        bu_ta_list = sorted(df_ta_date["BU"].dropna().unique())

        # ✅ 3) Multiselect BU (par défaut : toutes les BU de la période)
        selected_bu_ta = st.multiselect(
            "Filtrer les TA par BU",
            options=bu_ta_list,
            default=bu_ta_list,
            key=f"ta_bu_filter_{start_date}_{end_date}"
        )

        # ➕ Calculer le budget total sans appliquer le filtre de date
        df_ta_bu_only = df_ta_date[df_ta_date["BU"].isin(selected_bu_ta)]

        df_ta_bu_only["Budget Unitaire"] = df_ta_bu_only["Type de TA"].map(ta_budget_data).fillna(0)
        total_ca_budget_global = df_ta_bu_only["Budget Unitaire"].sum()

        # # 👉 APPLIQUE les filtres AVANT de faire ta_count
        # df_ta["Date de début"] = df_ta["Date de début"].apply(convert_trimestre_to_date)
        st.sidebar.write(f"Date d'Aujourd'hui : **{aujourd_hui.date().strftime('%d/%m/%Y')}**")
        # # 1. Filtrer d'abord
        # df_ta = df_ta[
        #     (df_ta["BU"].isin(selected_bu_ta)) &
        #     (df_ta["Date de début"] >= pd.Timestamp(start_date)) &
        #     (df_ta["Date de début"] <= pd.Timestamp(end_date))
        # ]
        # ✅ df_ta = TA filtrés date + BU
        df_ta = df_ta_date[df_ta_date["BU"].isin(selected_bu_ta)].copy()

        # Nettoyage des dates TBC
        aujourd_hui = pd.to_datetime(date.today())
        df_ta_valid = df_ta.copy()
        df_ta_valid["Date nettoyée"] = pd.to_datetime(df_ta_valid["Date de début"], errors="coerce")
        df_ta_valid = df_ta_valid[df_ta_valid["Date nettoyée"].notna() & (df_ta_valid["Date nettoyée"] <= aujourd_hui)]
        df_ta_valid["Budget Unitaire"] = df_ta_valid["Type de TA"].map(ta_budget_data).fillna(0)
        total_ca_realise = df_ta_valid["Budget Unitaire"].sum()

        # ➕ Répartition CA Réalisé par type de TA
        ca_realise_by_type = df_ta_valid.groupby("Type de TA")["Budget Unitaire"].sum().to_dict()
        ca_obs = ca_realise_by_type.get("observation", 0)
        ca_suivi = ca_realise_by_type.get("suivi & contrôle", 0)

        # 3. Calcul global vs filtré
        # nb_ta_global = df_ta_original.shape[0]
        # nb_ta_filtrées = df_ta.shape[0]
        #pourcentage_ta = (nb_ta_filtrées / nb_ta_global) * 100 if nb_ta_global != 0 else 0
        # Comptage global des TA totales et réalisées
        nb_ta_total = df_ta_original.shape[0]
        nb_ta_realisees = df_ta_valid.shape[0]
        pourcentage_ta = (nb_ta_realisees / nb_ta_total) * 100 if nb_ta_total != 0 else 0

        # Recalculer le ta_count à partir du df_ta filtré
        ta_count_filtered = df_ta.groupby(["BU", "Type de TA"]).agg({
            "Participant": "count",
            "Nb jours": "sum",
            "CA réalisé": "sum"
        }).reset_index().rename(columns={
            "Participant": "Nb TA",
            "Nb jours": "Nb jours TA",
            "CA réalisé": "CA (Réalisé)"
        })

        ta_count_filtered["CA"] = ta_count_filtered["Type de TA"].map(ta_budget_data).fillna(0) * ta_count_filtered["Nb TA"]

        # Ventilation par BU
        ventilation_ta = ta_count_filtered.groupby("BU")[["CA", "CA (Réalisé)"]].sum().reset_index()

        # TA par type
        obs_ta = ta_count_filtered[ta_count_filtered["Type de TA"] == "observation"].set_index("BU")["Nb TA"]
        suivi_ta = ta_count_filtered[ta_count_filtered["Type de TA"] == "suivi & contrôle"].set_index("BU")["Nb TA"]

        # Fusionner les deux colonnes
        ventilation_ta["Nb TA Observation"] = ventilation_ta["BU"].map(obs_ta).fillna(0).astype(int)
        ventilation_ta["Nb TA Suivi"] = ventilation_ta["BU"].map(suivi_ta).fillna(0).astype(int)

        # Réorganiser
        ventilation_ta = ventilation_ta[["BU", "Nb TA Observation", "Nb TA Suivi", "CA", "CA (Réalisé)"]]

        st.subheader("Indicateurs Clés")

        # Nettoyage : retirer ligne Total si déjà concaténée
        df_kpi_ta = ventilation_ta[ventilation_ta["BU"] != "Total"]

        # Calculs principaux
        total_ca_ta = df_kpi_ta["CA"].sum()
        total_ca_reel_ta = df_kpi_ta["CA (Réalisé)"].sum()
        total_ta_obs = df_kpi_ta["Nb TA Observation"].sum()
        total_ta_suivi = df_kpi_ta["Nb TA Suivi"].sum()
        total_ta = total_ta_obs + total_ta_suivi

        # Pourcentages
        percentage_used_ta = (total_ca_reel_ta / total_ca_ta * 100) if total_ca_ta != 0 else 0
        solde_ta = total_ca_budget_global - total_ca_realise
        percentage_remaining_ta = (solde_ta / total_ca_budget_global * 100) if total_ca_budget_global != 0 else 0

        def get_delta_class(delta):
            return "positive" if delta >= 0 else "negative"

        # Affichage sous forme de cartes
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="card">
                <h2>{format_montant(total_ca_budget_global)}</h2>
                <p>Total CA</p>
                <div class="delta positive">100%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <h2>{format_montant(total_ca_realise)}</h2>
                <p>Total CA Réalisé</p>
                <div class="delta {get_delta_class(total_ca_realise / total_ca_budget_global * 100)}">{(total_ca_realise / total_ca_budget_global * 100):.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("🔍 Détails CA Réalisé par type de TA"):
                total_ta_valid = len(df_ta_valid)
                nb_obs = len(df_ta_valid[df_ta_valid["Type de TA"] == "observation"])
                nb_suivi = len(df_ta_valid[df_ta_valid["Type de TA"] == "suivi & contrôle"])

                pct_obs = (nb_obs / total_ta_valid * 100) if total_ta_valid > 0 else 0
                pct_suivi = (nb_suivi / total_ta_valid * 100) if total_ta_valid > 0 else 0

                st.markdown(f"""
                <ul>
                    <li><strong>Observation</strong> : <strong>{ca_obs:,.0f} €</strong> — {nb_obs} TAs (<span style="color:green;">{pct_obs:.0f}%</span>)</li>
                    <li><strong>Suivi & Contrôle</strong> : <strong>{ca_suivi:,.0f} €</strong> — {nb_suivi} TAs (<span style="color:green;">{pct_suivi:.0f}%</span>)</li>
                </ul>
                """, unsafe_allow_html=True)



        with col3:
            st.markdown(f"""
            <div class="card">
                <h2>{format_montant(solde_ta)}</h2>
                <p>Solde Restant</p>
                <div class="delta {get_delta_class(percentage_remaining_ta)}">{percentage_remaining_ta:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="card">
                <h2>{nb_ta_realisees} / {nb_ta_total}</h2>
                <p>Nb Total de TA (Réalisées / Totales)</p>
                <div class="delta positive">{pourcentage_ta:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        # Comptage par type (Observation / Suivi)
        nb_obs_total = len(df_ta_original[df_ta_original["Type de TA"] == "observation"])
        nb_obs_realisees = len(df_ta_valid[df_ta_valid["Type de TA"] == "observation"])

        nb_suivi_total = len(df_ta_original[df_ta_original["Type de TA"] == "suivi & contrôle"])
        nb_suivi_realisees = len(df_ta_valid[df_ta_valid["Type de TA"] == "suivi & contrôle"])

        # =========================================
        # 🔹 Ligne 2 : Indicateurs par Type de TA
        # =========================================
        st.markdown("<br><hr><h4>Indicateurs par Type de TA</h4>", unsafe_allow_html=True)

        # --- Observation ---
        obs_budget = ta_budget_data.get("observation", 0) * total_ta_obs
        obs_reel = ca_obs
        obs_solde = obs_budget - obs_reel
        obs_pourcentage = (obs_reel / obs_budget * 100) if obs_budget != 0 else 0

        # --- Suivi & Contrôle ---
        suivi_budget = ta_budget_data.get("suivi & contrôle", 0) * total_ta_suivi
        suivi_reel = ca_suivi
        suivi_solde = suivi_budget - suivi_reel
        suivi_pourcentage = (suivi_reel / suivi_budget * 100) if suivi_budget != 0 else 0

        col_obs1, col_obs2, col_obs3, col_obs4 = st.columns(4)

        # ---- Observation ----
        with col_obs1:
            st.markdown(f"""
            <div class="card">
                <h3>Observation</h3>
                <h2>{format_montant(obs_budget)} €</h2>
                <p>CA Budget</p>
                <div class="delta positive">100%</div>
            </div>
            """, unsafe_allow_html=True)

        with col_obs2:
            st.markdown(f"""
            <div class="card">
                <h3>Observation</h3>
                <h2>{format_montant(obs_reel)} €</h2>
                <p>CA Réalisé</p>
                <div class="delta positive">{obs_pourcentage:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col_obs3:
            st.markdown(f"""
            <div class="card">
                <h3>Observation</h3>
                <h2>{format_montant(obs_solde)} €</h2>
                <p>Solde Restant</p>
                <div class="delta {get_delta_class(obs_solde)}">{100 - obs_pourcentage:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # --- Observation : Nb de TA ---
        with col_obs4:
            st.markdown(f"""
            <div class="card">
                <h3>Observation</h3>
                <h2>{nb_obs_realisees} / {nb_obs_total}</h2>
                <p>Nb de TA (Réalisées / Totales)</p>
                <div class="delta positive">{(nb_obs_realisees / nb_obs_total * 100 if nb_obs_total != 0 else 0):.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # ---- Suivi & Contrôle ----
        col_suivi1, col_suivi2, col_suivi3, col_suivi4 = st.columns(4)

        with col_suivi1:
            st.markdown(f"""
            <div class="card">
                <h3>Suivi & Contrôle</h3>
                <h2>{format_montant(suivi_budget)} €</h2>
                <p>CA Budget</p>
                <div class="delta positive">100%</div>
            </div>
            """, unsafe_allow_html=True)

        with col_suivi2:
            st.markdown(f"""
            <div class="card">
                <h3>Suivi & Contrôle</h3>
                <h2>{format_montant(suivi_reel)} €</h2>
                <p>CA Réalisé</p>
                <div class="delta positive">{suivi_pourcentage:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col_suivi3:
            st.markdown(f"""
            <div class="card">
                <h3>Suivi & Contrôle</h3>
                <h2>{format_montant(suivi_solde)} €</h2>
                <p>Solde Restant</p>
                <div class="delta {get_delta_class(suivi_solde)}">{100 - suivi_pourcentage:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        # --- Suivi & Contrôle : Nb de TA ---
        with col_suivi4:
            st.markdown(f"""
            <div class="card">
                <h3>Suivi & Contrôle</h3>
                <h2>{nb_suivi_realisees} / {nb_suivi_total}</h2>
                <p>Nb de TA (Réalisées / Totales)</p>
                <div class="delta positive">{(nb_suivi_realisees / nb_suivi_total * 100 if nb_suivi_total != 0 else 0):.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.subheader(" Ventilation TA par BU")
        # 🔁 Nouveau calcul : CA (Réalisé) basé sur budget unitaire
        df_ta_valid["CA (Budget Réalisé)"] = df_ta_valid["Type de TA"].map(ta_budget_data).fillna(0)

        # Regrouper par BU pour obtenir le CA total réalisé (calculé à partir du budget unitaire)
        ca_reel_par_bu = df_ta_valid.groupby("BU")["CA (Budget Réalisé)"].sum().reset_index()

        # Fusion avec le tableau existant
        ventilation_ta = ventilation_ta.drop(columns=["CA (Réalisé)"]).merge(ca_reel_par_bu, on="BU", how="left")

        # Renommer pour cohérence
        ventilation_ta = ventilation_ta.rename(columns={"CA (Budget Réalisé)": "CA (Réalisé)"})
        ventilation_ta["CA (Réalisé)"] = ventilation_ta["CA (Réalisé)"].fillna(0)


        # ➕ Ligne de total
        total_ta = pd.DataFrame({
            "BU": ["Total"],
            "Nb TA Observation": [ventilation_ta["Nb TA Observation"].sum()],
            "Nb TA Suivi": [ventilation_ta["Nb TA Suivi"].sum()],
            "CA": [ventilation_ta["CA"].sum()],
            "CA (Réalisé)": [ventilation_ta["CA (Réalisé)"].sum()]
        })

        ventilation_ta = pd.concat([ventilation_ta, total_ta], ignore_index=True)

        # Ajouter colonne Maintenu (à réaliser) = Budget - Réel
        ventilation_ta["Maintenu (à réaliser)"] = ventilation_ta["CA"] - ventilation_ta["CA (Réalisé)"]

        # Ajouter % Écart = Maintenu / Budget
        ventilation_ta["% Ecart"] = ventilation_ta.apply(
            lambda row: (row["Maintenu (à réaliser)"] / row["CA"]) * 100 if row["CA"] != 0 else 0,
            axis=1
        )

        # ✅ Appliquer les styles
        styled_ventilation = ventilation_ta.style \
            .apply(blue_row_style, axis=1) \
            .applymap(highlight_zeros, subset=["CA (Réalisé)", "Maintenu (à réaliser)", "% Ecart"]) \
            .format({
                "CA": "{:,.2f} €",
                "CA (Réalisé)": "{:,.2f} €",
                "Nb TA Observation": "{:.0f}",
                "Nb TA Suivi": "{:.0f}",
                "Maintenu (à réaliser)": "{:,.2f} €",
                "% Ecart": "{:.0f} %",
            })

        st.dataframe(styled_ventilation, use_container_width=True, hide_index=True)

        
        # ➕ Préparer les colonnes
        ventilation_ta["Solde Restant"] = ventilation_ta["CA"] - ventilation_ta["CA (Réalisé)"]

        # 📋 Détail des TA réalisées (jusqu'à aujourd’hui)
        df_ta_realisees = df_ta_valid[df_ta_valid["Date nettoyée"] <= pd.to_datetime("today")].copy()
        df_ta_realisees = df_ta_realisees.rename(columns={"Date nettoyée": "Date"})

        # Calcul du CA pour chaque ligne
        df_ta_realisees["CA (Budget Réalisé)"] = df_ta_realisees["Type de TA"].map(ta_budget_data).fillna(0)

        # Colonnes à afficher
        colonnes_a_afficher = ["BU", "Module", "Type de TA", "Participant", "Formateur", "CA (Budget Réalisé)", "Date"]

        st.subheader("📋 Détail des TA réalisées (jusqu'à aujourd’hui)")
        # 💅 Appliquer styles
        styled_ta_realisees = df_ta_realisees[colonnes_a_afficher].sort_values("Date").style \
            .apply(blue_row_style, axis=1) \
            .format({
                "CA (Budget Réalisé)": "{:,.0f} €",
                "Date": lambda d: d.strftime("%Y-%m-%d") if isinstance(d, pd.Timestamp) else d
            })

        st.dataframe(styled_ta_realisees, use_container_width=True, hide_index=True)




        # ➕ Graphique : Barres groupées pour Budget, Réel et Solde
        df_bar_ta = ventilation_ta[ventilation_ta["BU"] != "Total"][["BU", "CA", "CA (Réalisé)", "Solde Restant"]]
        df_bar_ta_long = df_bar_ta.melt(id_vars="BU", var_name="Type", value_name="Montant (€)")

        st.subheader("Comparatif CA / CA réalisé / Maintenu à réaliser par BU (TA)")
        fig_ta = px.bar(
            df_bar_ta_long,
            x="BU",
            y="Montant (€)",
            color="Type",
            barmode="group",
            text_auto=".2s",
            color_discrete_map={
                "CA": "#0033A0",       # Bleu
                "CA (Réalisé)": "#66B2FF",       # Rouge clair
                "Solde Restant": "#66BB66"     # Vert
            }
        )
        fig_ta.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_ta, use_container_width=True)
        # 🔹 Courbe Évolution CA vs Réel cumulé (TA)

        # Budget : toutes les TA (df_ta)
        df_budget_monthly = df_ta.copy()
        df_budget_monthly["Mois"] = df_budget_monthly["Date de début"].dt.to_period("M").dt.to_timestamp()
        df_budget_monthly["CA"] = df_budget_monthly["Type de TA"].map(ta_budget_data).fillna(0)

        # Réel : uniquement les lignes valides (df_ta_valid)
        df_reel_monthly = df_ta_valid.copy()
        df_reel_monthly["Mois"] = df_reel_monthly["Date nettoyée"].dt.to_period("M").dt.to_timestamp()
        df_reel_monthly["Budget Unitaire"] = df_reel_monthly["Type de TA"].map(ta_budget_data).fillna(0)
        df_reel_monthly["CA (Réalisé)"] = df_reel_monthly["Budget Unitaire"]  # ✅ c’est le budget réel jusqu’à date

        # Cumul Budget
        df_budget_grouped = df_budget_monthly.groupby("Mois")["CA"].sum().sort_index().cumsum().reset_index()
        df_budget_grouped = df_budget_grouped.rename(columns={"CA": "CA Cumulé"})

        # Cumul Réel (basé sur budget unitaire des TA réalisées)
        df_reel_grouped = df_reel_monthly.groupby("Mois")["CA (Réalisé)"].sum().sort_index().cumsum().reset_index()
        df_reel_grouped = df_reel_grouped.rename(columns={"CA (Réalisé)": "CA réalisé Cumulé"})

        # Fusion
        df_grouped_ta = pd.merge(df_budget_grouped, df_reel_grouped, on="Mois", how="outer").fillna(method="ffill").fillna(0)

        # Format long pour graphique
        df_ta_long = df_grouped_ta.melt(id_vars="Mois", var_name="Type", value_name="Montant (€)")

        # Affichage
        st.subheader("📈 Évolution CA vs CA réalisé cumulé (TA)")
        fig_ta = px.line(
            df_ta_long,
            x="Mois",
            y="Montant (€)",
            color="Type",
            markers=True,
            text="Montant (€)",
            color_discrete_map={
                "CA Cumulé": "#0033A0",
                "CA réalisé Cumulé": "#66B2FF"
            }
        )
        fig_ta.update_traces(texttemplate="%{text:,.0f} €", textposition="top right")
        fig_ta.update_layout(yaxis_title="Montant (€)", xaxis_title="Mois")
        st.plotly_chart(fig_ta, use_container_width=True)


        # from datetime import date

        # # Affiche les colonnes disponibles pour debug
        # st.write("Colonnes dans df_ta :", df_ta.columns.tolist())

        # # Date du jour
        # aujourd_hui = pd.to_datetime(date.today())

        # # Nettoyer les dates
        # df_ta["Date nettoyée"] = pd.to_datetime(df_ta["Date de début"], errors="coerce")  # ← adapte ici selon ton vrai nom de colonne

        # # Filtrer les dates connues jusqu'à aujourd'hui
        # df_ta_valid = df_ta[df_ta["Date nettoyée"].notna() & (df_ta["Date nettoyée"] <= aujourd_hui)]

        # # Total CA Réalisé réel
        # total_ca_reel = df_ta_valid["CA réalisé"].sum()

        # # Affichage
        # st.subheader("📅 Total CA Réalisé (jusqu'à aujourd'hui)")
        # st.write(f"Aujourd'hui : **{aujourd_hui.date().strftime('%d/%m/%Y')}**")
        # st.metric("Total CA Réalisé", f"{total_ca_reel:,.2f} €")
    # # =========================================
    # # Onglet 3 : Prestations Ingénierie
    # with tab3:
    #     st.markdown("### Suivi des prestations Ingénierie")

    #     # --- Charger les données depuis Excel ---
    #     df = pd.read_excel("JL_PAC WSA Consultants Externes 2026 (5).xlsx", sheet_name="Ingénierie 2026 WSA", header=1)
    #     df = df[["Intervenant", "Mois", "Nb Jours"]].dropna()

    #     pu_ingenierie = {
    #         "Allison BEOLET": 500,
    #         "Julie LARUE": 650,
    #         "Béatrice CHAUSSON": 350,
    #         "Sonia PEREZ": 200,
    #         "Sharlen MICIELI": 500,
    #         "Anas Zahi": 550,
    #         "xx": 500
    #     }

    #     df = df[df["Intervenant"].isin(pu_ingenierie.keys())]
    #     df["PU"] = df["Intervenant"].map(pu_ingenierie)
    #     df["Coût (€)"] = df["Nb Jours"] * df["PU"]
    #     df["Mois"] = pd.to_datetime(df["Mois"], errors="coerce")
    #     df["Coût (€)"] = df["Coût (€)"].round(2)

    #     # --- TOTAL BUDGET (fixe) ---
    #     total_ca_budget = df["Coût (€)"].sum()

    #     # --- Date d'aujourd'hui ---
    #     today = pd.Timestamp.today()

    #     # --- Widget filtre de date, avec aujourd’hui par défaut ---
    #     min_date, max_date = df["Mois"].min(), df["Mois"].max()
    #     default_end = today if today <= max_date else max_date
    #     start_date, end_date = st.date_input("📅 Filtrer le CA Réalisé", [min_date, default_end], key="date_range_ingenierie")

    #     # --- Appliquer le filtre pour CA réalisé ---
    #     df_real = df[
    #         (df["Mois"] >= pd.Timestamp(start_date)) &
    #         (df["Mois"] <= pd.Timestamp(end_date))
    #     ]
    #     total_ca_realise = df_real["Coût (€)"].sum()

    #     # --- Calculs ---
    #     solde = total_ca_budget - total_ca_realise
    #     pourcentage_solde = (solde / total_ca_budget) * 100 if total_ca_budget != 0 else 0
    #     pourcentage_realise = (total_ca_realise / total_ca_budget) * 100 if total_ca_budget != 0 else 0

    #     nb_prestations = len(df)
    #     nb_realisees = len(df_real)
    #     pourcentage_nb = (nb_realisees / nb_prestations) * 100 if nb_prestations != 0 else 0

    #     # ▶️ Nombre total de jours
    #     nb_jours_budget = df["Nb Jours"].sum()
    #     nb_jours_realises = df_real["Nb Jours"].sum()
    #     pourcentage_jours = (nb_jours_realises / nb_jours_budget) * 100 if nb_jours_budget != 0 else 0

    #     def get_delta_class(delta):
    #         return "positive" if delta >= 0 else "negative"

    #     # --- Cartes indicateurs ---
    #     col1, col2, col3, col4, col5 = st.columns(5)
    #     with col1:
    #         st.markdown(f"""
    #         <div class="card">
    #             <h2>{total_ca_budget:,.2f} €</h2>
    #             <p>Total CA</p>
    #             <div class="delta positive">100%</div>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     with col2:
    #         st.markdown(f"""
    #         <div class="card">
    #             <h2>{total_ca_realise:,.2f} €</h2>
    #             <p>Total CA Réalisé</p>
    #             <div class="delta {get_delta_class(pourcentage_realise)}">{pourcentage_realise:.0f}%</div>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     with col3:
    #         st.markdown(f"""
    #         <div class="card">
    #             <h2>{solde:,.2f} €</h2>
    #             <p>Solde Restant</p>
    #             <div class="delta {get_delta_class(pourcentage_solde)}">{pourcentage_solde:.0f}%</div>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     with col4:
    #         st.markdown(f"""
    #         <div class="card">
    #             <h2>{nb_realisees} / {nb_prestations}</h2>
    #             <p>Nb d'Ingénieries</p>
    #             <div class="delta positive">{pourcentage_nb:.0f}%</div>
    #         </div>
    #         """, unsafe_allow_html=True)
    #     with col5:
    #         st.markdown(f"""
    #         <div class="card">
    #             <h2>{int(nb_jours_realises)} / {int(nb_jours_budget)}</h2>
    #             <p>Nb Jours Réalisés</p>
    #             <div class="delta positive">{pourcentage_jours:.0f}%</div>
    #         </div>
    #         """, unsafe_allow_html=True)

    #     # 🔽 Colonnes à afficher (tu peux les adapter selon ton fichier)
    #     colonnes_a_afficher = ["Intervenant", "Mois", "Nb Jours", "PU", "Coût (€)"]

    #     # 🧾 Appliquer style et formats
    #     styled_prestations = df[colonnes_a_afficher].sort_values("Mois").style \
    #         .apply(blue_row_style, axis=1) \
    #         .format({
    #             "Coût (€)": "{:,.0f} €",
    #             "PU": "{:,.0f} €",
    #             "Nb Jours": "{:.0f}",
    #             "Mois": lambda d: d.strftime("%Y-%m") if isinstance(d, pd.Timestamp) else d
    #         })

    #     # 📋 Affichage
    #     st.markdown("### Détail des prestations")
    #     st.dataframe(styled_prestations, use_container_width=True)

        
    with tab3:
        # Création HTML dynamique depuis df_summary
        table_html = """
        <style>
            .mission-info-table {
                border: 2px solid #0033A0;
                border-collapse: collapse;
                width: 100%;
                font-size: 0.9rem;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                margin-top: 20px;
            }
            .mission-info-table th, .mission-info-table td {
                border: 1px solid #ccc;
                padding: 8px 12px;
                text-align: center;
            }
            .mission-info-table th {
                background-color: #0033A0;
                color: white;
                font-weight: bold;
            }
            .mission-info-table td:first-child {
                background-color: rgba(0, 51, 160, 0.1);
                font-weight: bold;
                text-align: left;
            }
            .mission-info-table tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            .mission-info-table tr:hover {
                background-color: #e0ecff;
            }
        </style>
        <table class="mission-info-table">
            <thead>
                <tr>
        """
        # --- Chargement de la feuille Participants (si ce n'est pas déjà fait)
        if "calendar_file" in st.session_state:
            df_participants = pd.read_excel(st.session_state["calendar_file"], sheet_name="BDD Participants 2026", header=2)

        # --- Mise en forme avec couleurs personnalisées
        def highlight_type(row):
            color = ""
            if row["Type"] == "TA":
                color = "background-color: #FFCC80;"  # orange clair
            elif row["Type"] == "Formation":
                color = "background-color: #64B5F6;"  # bleu clair
            elif row["Type"] == "Ingénierie":
                color = "background-color: #E8F5E9;"  # vert très pâle
            elif row["Type"] == "TOTAL":
                color = "background-color: #BDBDBD;"  # gris clair
            return [color] * len(row)
        
        def normalize_bu(bu):
            if isinstance(bu, str):
                return bu.strip().upper().replace("É", "E")  # Pour éviter accents
            return bu

        df_form["BU"] = df_form["BU"].apply(normalize_bu)
        df_ta["BU"] = df_ta["BU"].apply(normalize_bu)

        st.subheader("Ventilation Budgets T1 par Groupes")

        # --- INPUT modifiable : Budget total Ingénierie ---
        budget_t1_inge = st.number_input("💼 Budget T1 - Ingénierie (modifiable)", value=101000, step=1000)

        # === On ne garde QUE les groupes présents dans Formations 2026 ===
        df_form["Groupe_clean"] = df_form["Groupes"].apply(_norm_groupe)
        df_ta["Groupe_clean"]   = df_ta["BU"].apply(_norm_groupe)   # df_ta["BU"] = colonne "Groupe" du TA
        groupes_list = sorted(g for g in df_form["Groupe_clean"].dropna().unique())

        # Budget Formation par groupe
        formation_budget = (
            df_form[df_form["Groupe_clean"].isin(groupes_list)]
            .groupby("Groupe_clean")["CA"]
            .apply(lambda x: pd.to_numeric(x.astype(str).str.replace("€", "").str.replace(",", ""), errors="coerce").sum())
            .to_dict()
        )

        # Budget TA par groupe (restreint aux groupes de Formations 2026)
        df_ta["CA"] = df_ta["Type de TA"].map(ta_budget_data).fillna(0)
        ta_budget = (
            df_ta[df_ta["Groupe_clean"].isin(groupes_list)]
            .groupby("Groupe_clean")["CA"].sum().to_dict()
        )

        # Ingénierie répartie au prorata du nombre de formations par groupe
        form_count_by_grp = df_form[df_form["Groupe_clean"].isin(groupes_list)]["Groupe_clean"].value_counts().to_dict()
        total_formations = sum(form_count_by_grp.values())
        if total_formations > 0:
            inge_per_grp = {g: round((form_count_by_grp.get(g, 0) / total_formations) * budget_t1_inge, 2) for g in groupes_list}
        else:
            inge_per_grp = {g: 0 for g in groupes_list}

        # Construction du tableau par groupe
        data = {"Type": ["Ingénierie", "TA", "Formation", "TOTAL"]}
        for g in groupes_list:
            data[g] = [
                inge_per_grp.get(g, 0),
                ta_budget.get(g, 0),
                formation_budget.get(g, 0),
                inge_per_grp.get(g, 0) + ta_budget.get(g, 0) + formation_budget.get(g, 0),
            ]

        df_budget = pd.DataFrame(data)
        df_budget["TOTAL"] = df_budget.apply(
            lambda row: budget_t1_inge if row["Type"] == "Ingénierie"
            else sum(x for x in row[groupes_list] if isinstance(x, (int, float))),
            axis=1
        )

        # --- Conversion des colonnes numériques uniquement (évite Type qui est str)
        cols_to_format = df_budget.columns.difference(['Type'])
        df_budget[cols_to_format] = df_budget[cols_to_format].apply(pd.to_numeric, errors='coerce')

        # styled_budget = df_budget.style \
        #     .format(lambda x: f"{x:,.0f} €" if isinstance(x, (int, float)) else x, subset=cols_to_format) \
        #     .apply(highlight_type, axis=1)



        # # --- Affichage
        # st.dataframe(styled_budget)
        # --- Formatage des montants en € pour affichage
        df_budget_display = df_budget.copy()
        df_budget_display.rename(columns={"ALL": "MAISONS"}, inplace=True)

        for col in df_budget_display.columns[1:]:  # Sauf colonne "Type"
            df_budget_display[col] = df_budget_display[col].apply(
                lambda x: f"{x:,.0f}".replace(",", " ") + " €" if pd.notnull(x) and isinstance(x, (int, float)) else x
            )
                # En-têtes
        for col in df_budget_display.columns:
            table_html += f"<th>{col}</th>"
        table_html += "</tr></thead><tbody>"

        # Lignes avec surbrillance par "Type"
        row_colors = {
            "TA": "#FFE0B2",         # jaune clair
            "Formation": "#E3F2FD",  # bleu clair
            "Ingénierie": "#E8F5E9", # vert très clair
            "TOTAL": "#CECECE"       # beige clair
        }

        for _, row in df_budget_display.iterrows():
            row_type = row["Type"]
            bg_color = row_colors.get(row_type, "")
            style = f' style="background-color: {bg_color};"' if bg_color else ""
            
            table_html += "<tr>"
            for val in row:
                table_html += f"<td{style}>{val}</td>"
            table_html += "</tr>"

        table_html += "</tbody></table>"

        # --- Affichage final
        st.markdown(table_html, unsafe_allow_html=True)

        def style_table(df):
            row_colors = {
                "Nbre de formations": "#E3F2FD",
                "Nombre de formateurs": "#BBDEFB",
                "Nbre de TA Observation": "#90CAF9",
                "Nbre de TA Suivi": "#64B5F6"
            }

            def highlight_rows(row):
                libelle = row.iloc[0]  # Première colonne contient les libellés
                color = row_colors.get(libelle, "")
                return [f"background-color: {color}" if color else "" for _ in row]

            return df.style.apply(highlight_rows, axis=1)

        with st.expander("Formations & Formateurs", expanded=True):
            
            st.subheader("Formations & Formateurs")
            
            # Fonction de normalisation des BU
            def normalize_bu(bu):
                if isinstance(bu, str):
                    return bu.strip().upper().replace("É", "E")
                return bu
            # Correspondance BU pour regrouper les participants dans les bonnes zones
            bu_mapping = {
                "ALLEMAGNE": "ALLEMAGNE",
                "APAC - CHINE": "APAC CHINE",
                "ESPAGNE": "ESPAGNE",
                "EUROPE DU NORD": "EUROPE DU NORD",
                "FRANCE": "FRANCE",
                "FRANCE_TÉLÉVENTE": "FRANCE",
                "FRANCE WEISS": "FRANCE",
                "FRANCE  KAM GAM": "FRANCE",
                "FRANCE KAM GAM": "FRANCE",
                "ITALIE": "ITALIE",
                "JAPON": "JAPON",
                "RETAIL INTERNATIONAL": "RETAIL",
                "CORPORATE GIFTING": "RETAIL",
                "MAISONS": "ALL",
                "USA - CANADA": "USA CANADA"
            }
            bu_mapping_norm = {normalize_bu(k): normalize_bu(v) for k, v in bu_mapping.items()}

            # === Regroupement par GROUPES (colonne "Groupes" de Formations 2026) ===
            df_form["Groupe_clean"] = df_form["Groupes"].apply(_norm_groupe)
            df_ta["Groupe_clean"]   = df_ta["BU"].apply(_norm_groupe)
            groupes_list = sorted(g for g in df_form["Groupe_clean"].dropna().unique())

            form_counts = df_form[df_form["Groupe_clean"].isin(groupes_list)].groupby("Groupe_clean").size()
            formateurs  = df_form[df_form["Groupe_clean"].isin(groupes_list)].groupby("Groupe_clean")["Formateur 1"].nunique()

            ta_obs   = df_ta[df_ta["Type de TA"].str.lower().str.contains("observation", na=False)]
            ta_suivi = df_ta[df_ta["Type de TA"].str.lower().str.contains("suivi", na=False)]
            ta_obs_counts   = ta_obs[ta_obs["Groupe_clean"].isin(groupes_list)].groupby("Groupe_clean").size()
            ta_suivi_counts = ta_suivi[ta_suivi["Groupe_clean"].isin(groupes_list)].groupby("Groupe_clean").size()

            participants_dict = get_nb_participants_par_groupe(df_participants, groupes_list)

            data_summary = {
                "WSA 2026": [
                    "Nbre de formations", "Nombre de formateurs",
                    "Nbre de TA Observation", "Nbre de TA Suivi", "Nombre de participants",
                ]
            }
            for g in groupes_list:
                data_summary[g] = [
                    int(form_counts.get(g, 0)),
                    int(formateurs.get(g, 0)),
                    int(ta_obs_counts.get(g, 0)),
                    int(ta_suivi_counts.get(g, 0)),
                    int(participants_dict.get(g, 0)),
                ]

            data_summary["TOTAL"] = [
                int(form_counts.sum()),
                int(df_form[df_form["Groupe_clean"].isin(groupes_list)]["Formateur 1"].nunique()),
                int(ta_obs[ta_obs["Groupe_clean"].isin(groupes_list)].shape[0]),
                int(ta_suivi[ta_suivi["Groupe_clean"].isin(groupes_list)].shape[0]),
                get_nb_participants_distinct_total_via_groupes(df_form, df_participants),
            ]

            df_summary = pd.DataFrame(data_summary)

            # Création HTML dynamique depuis df_summary
            table_html = """
            <style>
                .mission-info-table {
                    border: 2px solid #0033A0;
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 0.9rem;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    margin-top: 20px;
                }
                .mission-info-table th, .mission-info-table td {
                    border: 1px solid #ccc;
                    padding: 8px 12px;
                    text-align: center;
                }
                .mission-info-table th {
                    background-color: #0033A0;
                    color: white;
                    font-weight: bold;
                }
                .mission-info-table td:first-child {
                    background-color: rgba(0, 51, 160, 0.1);
                    font-weight: bold;
                    text-align: left;
                }
                .mission-info-table tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                .mission-info-table tr:hover {
                    background-color: #e0ecff;
                }
            </style>
            <table class="mission-info-table">
                <thead>
                    <tr>
            """

            # Ajout des en-têtes de colonnes
            for col in df_summary.columns:
                table_html += f"<th>{col}</th>"
            table_html += "</tr></thead><tbody>"

            # Ajout des lignes
            for i in range(len(df_summary)):
                table_html += "<tr>"
                for col in df_summary.columns:
                    table_html += f"<td>{df_summary[col].iloc[i]}</td>"
                table_html += "</tr>"

            table_html += "</tbody></table>"

            # Affichage dans Streamlit
            st.markdown(table_html, unsafe_allow_html=True)

            # Extraction des données (assure-toi que les valeurs sont bien numériques)
            bu_cols = [col for col in df_budget.columns if col not in ["Type", "TOTAL"]]

            fig = go.Figure()
            # Dictionnaire des couleurs par type
            color_map = {
                "Ingénierie": "#80CBC4",   # Vert clair
                "TA": "#FB8C00",           # Jaune pâle
                "Formation": "#64B5F6"     # Bleu clair
            }
            for type_ in ["Formation", "TA", "Ingénierie"]:
                fig.add_trace(go.Bar(
                    x=bu_cols,
                    y=df_budget[df_budget["Type"] == type_][bu_cols].values.flatten(),
                    name=type_,
                    marker_color=color_map[type_]
                ))

            fig.update_layout(
                barmode='stack',
                title="Répartition des Budgets par BU (empilé)",
                xaxis_title="BU",
                yaxis_title="Montant (€)",
                legend_title="Type",
                template="plotly_white",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)









