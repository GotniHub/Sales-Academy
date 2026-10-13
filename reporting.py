"""Shared counting rules for all Sales Academy reports."""
import pandas as pd


def normalize_text(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).split()).upper()


def prepare_formations(df):
    """Accept the original Excel header while displaying its actual meaning."""
    return df.rename(columns={"Nb participant": "Nb participations"}).copy()


def clean_ta(df):
    """Keep real Observation/Suivi records, not Excel padding or stray cells."""
    out = df.copy()
    out["Type de TA"] = out["Type de TA"].fillna("").astype(str).str.strip().str.lower()
    out["Type de TA"] = out["Type de TA"].replace({"suivi & contrôle": "suivi"})
    # A planned TA may have a TBC date or participant. Its type identifies it.
    return out[out["Type de TA"].isin(["observation", "suivi"])].copy()


def participant_rows(df, groups=None):
    if df is None:
        return pd.DataFrame(columns=["__grp", "__nom", "__pre"])
    out = df.copy()
    out["__grp"] = out["Groupes"].map(normalize_text)
    out["__nom"] = out["Nom"].map(normalize_text)
    out["__pre"] = out["Prénom"].map(normalize_text)
    out = out[out["__grp"].ne("")]
    if groups is not None:
        allowed = {normalize_text(g) for g in groups if normalize_text(g)}
        out = out[out["__grp"].isin(allowed)]
    return out


def counts_by_group(df, groups=None, unique=False):
    rows = participant_rows(df, groups)
    if unique:
        rows = rows[rows["__nom"].ne("") | rows["__pre"].ne("")]
        rows = rows.drop_duplicates(["__grp", "__nom", "__pre"])
    return rows.groupby("__grp").size().to_dict()


def count_total(df_form, df_participants, unique=False):
    rows = participant_rows(df_participants, df_form["Groupes"])
    if unique:
        rows = rows[rows["__nom"].ne("") | rows["__pre"].ne("")]
        rows = rows.drop_duplicates(["__nom", "__pre"])
    return len(rows)


def counts_by_bu(df_form, df_participants, unique=False):
    forms = df_form.assign(__bu=df_form["BU"].map(normalize_text))
    counts = {}
    for bu, forms_bu in forms.groupby("__bu"):
        rows = participant_rows(df_participants, forms_bu["Groupes"])
        if unique:
            rows = rows[rows["__nom"].ne("") | rows["__pre"].ne("")]
            rows = rows.drop_duplicates(["__nom", "__pre"])
        counts[bu] = len(rows)
    return counts


def add_unique_participants(table, df_form, df_participants, bu_column="BU"):
    """Unique total must be computed globally, never summed across BUs."""
    out = table.copy()
    if df_participants is None:
        out["Nb Participants"] = pd.NA
    else:
        counts = counts_by_bu(df_form, df_participants, unique=True)
        out["Nb Participants"] = out[bu_column].map(normalize_text).map(counts).fillna(0).astype(int)
    return out
