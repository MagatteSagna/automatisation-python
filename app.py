import logging

import streamlit as st

from src.pipeline import clean_upload, organize_folder
from src.reports import format_report
from src.utils import setup_logging

OUTPUT_DIR = "data/output"

setup_logging()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Automatisation Python", page_icon="🧹")


def show_banner():
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #C2185B, #EC407A);
                    padding: 1.3rem 1.6rem; border-radius: 14px; color: white; margin-bottom: 1rem;">
            <div style="font-size: 1.8rem; font-weight: 700;">🧹 Outil d'automatisation</div>
            <div style="opacity: 0.95; margin-top: 0.2rem;">
                Nettoyage de fichiers Excel/CSV et classement de documents
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_sidebar():
    with st.sidebar:
        st.header("Comment ça marche ?")
        st.markdown(
            "1. **Charge** un fichier Excel ou CSV\n"
            "2. **Lance** le traitement\n"
            "3. **Consulte** le rapport"
        )
        st.subheader("Règles de nettoyage")
        st.markdown(
            "- Espaces superflus supprimés\n"
            "- E-mails en minuscules\n"
            "- Noms et prénoms en format Titre\n"
            "- Doublons supprimés (la 1re ligne est gardée)\n"
            "- E-mails invalides signalés, **non supprimés**\n"
            "- Le fichier d'origine n'est jamais modifié"
        )
        st.caption("Journal : logs/automatisation.log")


def show_cleaning_report(r: dict):
    st.success("Traitement terminé.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Lignes lues", r["lignes_lues"], border=True)
    c2.metric("Lignes exportées", r["lignes_exportees"], border=True)
    c3.metric("Doublons supprimés", r["doublons_supprimes"], border=True)

    c4, c5, c6 = st.columns(3)
    c4.metric("Champs manquants", sum(r["champs_manquants"].values()), border=True)
    c5.metric("E-mails invalides", r["emails_invalides"], border=True)
    c6.metric("Durée", f"{r['duree_secondes']} s", border=True)

    if r["champs_manquants"]:
        detail = ", ".join(f"**{col}** : {n}" for col, n in r["champs_manquants"].items())
        st.info(f"Champs manquants par colonne : {detail}")
    if r["lignes_emails_invalides"]:
        lignes = ", ".join(str(n) for n in r["lignes_emails_invalides"])
        st.warning(
            f"E-mails invalides aux lignes Excel : {lignes}. "
            "Ils sont signalés mais conservés dans le fichier exporté."
        )

    with st.expander("Fichiers générés"):
        st.markdown("\n".join(f"- `{f}`" for f in r["fichiers_generes"]))
    with st.expander("Rapport texte complet"):
        st.code(format_report(r), language=None)


def show_organizing_report(r: dict):
    st.success("Classement terminé.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Traités", r["fichiers_traites"], border=True)
    c2.metric("Classés", r["fichiers_classes"], border=True)
    c3.metric("Erreurs", len(r["erreurs"]), border=True)
    c4.metric("Durée", f"{r['duree_secondes']} s", border=True)

    for erreur in r["erreurs"]:
        st.error(erreur)

    with st.expander("Fichiers générés"):
        st.markdown("\n".join(f"- `{f}`" for f in r["fichiers_generes"]))
    with st.expander("Rapport texte complet"):
        st.code(format_report(r), language=None)


show_banner()
show_sidebar()

tab_clean, tab_sort = st.tabs(["🧹 Nettoyer un fichier", "📂 Classer des fichiers"])

# ---------- Onglet 1 : nettoyage ----------
with tab_clean:
    with st.container(border=True):
        st.subheader("1. Charger un fichier")
        uploaded = st.file_uploader("Choisis un fichier .csv ou .xlsx", type=["csv", "xlsx"])
        if uploaded is None:
            st.info("Aucun fichier chargé pour l'instant.")
        else:
            st.write(f"Fichier chargé : **{uploaded.name}** ({uploaded.size} octets)")
            if uploaded.name.lower().endswith("_nettoye.xlsx"):
                st.warning("Ce fichier semble avoir déjà été nettoyé. Charge plutôt le fichier d'origine.")

    with st.container(border=True):
        st.subheader("2. Lancer le traitement")
        if st.button("Lancer le nettoyage", type="primary", disabled=uploaded is None):
            with st.spinner("Traitement en cours..."):
                try:
                    st.session_state["rapport_nettoyage"] = clean_upload(
                        uploaded.name, uploaded.getvalue(), OUTPUT_DIR
                    )
                except (FileNotFoundError, ValueError) as e:
                    st.session_state.pop("rapport_nettoyage", None)
                    st.error(str(e))
                except Exception:
                    st.session_state.pop("rapport_nettoyage", None)
                    logger.exception("Erreur inattendue pendant le nettoyage")
                    st.error("Erreur inattendue. Détails dans le journal : logs/automatisation.log")

    if "rapport_nettoyage" in st.session_state:
        st.subheader("3. Résultat")
        show_cleaning_report(st.session_state["rapport_nettoyage"])

# ---------- Onglet 2 : classement ----------
with tab_sort:
    with st.container(border=True):
        st.subheader("Classer et renommer des fichiers")
        dossier = st.text_input("Dossier à classer", value="data/input/fichiers_a_classer")
        col_mode, col_dest = st.columns(2)
        mode = col_mode.radio("Classer par", ["extension", "date"], horizontal=True)
        destination = col_dest.text_input("Dossier de destination", value="data/output/classes")
        deplacer = st.checkbox("Déplacer les fichiers (sinon, ils sont copiés)")
        if deplacer:
            st.warning("Les fichiers d'origine seront déplacés : ils ne seront plus dans le dossier source.")

        if st.button("Lancer le classement", type="primary"):
            with st.spinner("Classement en cours..."):
                try:
                    st.session_state["rapport_classement"] = organize_folder(dossier, destination, mode, deplacer)
                except (FileNotFoundError, ValueError) as e:
                    st.session_state.pop("rapport_classement", None)
                    st.error(str(e))
                except Exception:
                    st.session_state.pop("rapport_classement", None)
                    logger.exception("Erreur inattendue pendant le classement")
                    st.error("Erreur inattendue. Détails dans le journal : logs/automatisation.log")

    if "rapport_classement" in st.session_state:
        st.subheader("Résultat")
        show_organizing_report(st.session_state["rapport_classement"])