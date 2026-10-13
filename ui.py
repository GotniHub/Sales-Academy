"""Visual identity shared by the home page and the reporting workspace."""
from html import escape
from pathlib import Path

import streamlit as st
import plotly.io as pio

ROOT = Path(__file__).resolve().parent


def apply_theme():
    st.markdown(f"<style>{(ROOT / 'assets' / 'academy.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    pio.templates['academy'] = pio.templates['plotly_white']
    pio.templates['academy'].layout.update(
        font=dict(family='Arial, sans-serif', color='#34445E', size=13),
        colorway=['#0033A0', '#41A9B9', '#8C6AC8', '#E9A23B'],
        paper_bgcolor='white', plot_bgcolor='white',
        margin=dict(l=24, r=24, t=64, b=36),
        xaxis=dict(gridcolor='#E8EDF5', zeroline=False),
        yaxis=dict(gridcolor='#E8EDF5', zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', orientation='h', y=-0.2),
    )
    pio.templates.default = 'academy'


def page_header(title, subtitle, section='ESPACE DE PILOTAGE'):
    st.markdown(
        f'<div class="academy-hero"><div class="academy-eyebrow">{escape(section)}</div>'
        f'<h1>{escape(title)}</h1><p>{escape(subtitle)}</p></div>',
        unsafe_allow_html=True,
    )


def audience_metrics(df_form, df_participants):
    from reporting import count_total, participant_rows
    st.caption('Source : BDD Participants 2026. Participations : inscriptions, doublons inclus. Participants : personnes uniques par Nom + Prénom, dans les groupes sélectionnés.')
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Nombre de participations', count_total(df_form, df_participants) if df_participants is not None else '—')
    with col2:
        st.metric('Nombre de participants uniques', count_total(df_form, df_participants, unique=True) if df_participants is not None else '—')
    if df_participants is None:
        st.info('La feuille BDD Participants 2026 est indisponible. Le nombre de participants uniques ne peut pas être calculé.')
    else:
        rows = participant_rows(df_participants, df_form['Groupes'])
        missing = int((rows['__nom'].eq('') & rows['__pre'].eq('')).sum())
        if missing:
            st.caption(f'{missing} inscription(s) sans Nom ni Prénom : incluses dans les participations, exclues des personnes uniques.')
