import streamlit as st
from ui import apply_theme, page_header, ROOT

st.set_page_config(page_title="Sales Academy | Accueil", page_icon="📊", layout="wide")
apply_theme()
st.logo(str(ROOT / "Logo Sales Academy.png"))
st.image(str(ROOT / "Logo Sales Academy.png"), width=175)
page_header(
    "Pilotez votre Sales Academy",
    "Un seul espace pour préparer vos données, suivre les formations et analyser vos budgets.",
    "SALES ACADEMY · ADVENT+ AFRICA",
)
st.page_link("pages/Automatisation.py", label="Ouvrir l’espace de pilotage", icon="📊")
st.subheader("De votre planning à vos rapports")
cards = [
    ("01", "Préparez vos données", "Importez le planning Excel et ajustez les tarifs de formation."),
    ("02", "Suivez l’activité", "Consultez les formations, les TA, les participations et les personnes uniques."),
    ("03", "Analysez vos budgets", "Comparez le prévu et le réalisé par business unit et par groupe."),
]
for column, (number, title, description) in zip(st.columns(3), cards):
    with column:
        st.markdown(
            f'<div class="academy-step"><span>{number}</span><h3>{title}</h3><p>{description}</p></div>',
            unsafe_allow_html=True,
        )
st.caption("Source : planning Excel · Formations 2026, TA 2026 et BDD Participants 2026.")
