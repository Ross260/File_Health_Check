import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def main():
    # Injection de CSS pour le design du titre
    st.markdown("""
        <style>
        .title-container {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .main-title {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 3rem !important;
            font-weight: 800;
            margin-bottom: 0px;
            letter-spacing: -1px;
        }
        .sub-title {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 300;
        }
        /* Style pour l'icône de pouls */
        .pulse {
            display: inline-block;
            margin-right: 15px;
            animation: pulse-animation 2s infinite;
        }
        @keyframes pulse-animation {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        </style>
        
        <div class="title-container">
            <h1 class="main-title">
                <span class="pulse">🏥</span> File Health Check
            </h1>
            <p class="sub-title">Diagnostic et visualisation de la qualité de vos datasets</p>
        </div>
    """, unsafe_allow_html=True)

# Création d'une fonction isolée pour la lecture réelle, décorée avec le cache
# Cela permet de ne pas mettre en cache toute la barre latérale (sidebar)
@st.cache_data(show_spinner="Chargement des données en cours...")
def fetch_and_parse_data(file_or_url):
    # engine='pyarrow' : moteur le plus rapide actuellement pour les CSV
    return pd.read_csv(file_or_url, engine='pyarrow')

def load_data():
    st.sidebar.title("Importez vos données")
    source = st.sidebar.radio("Choisir la source :", ["CSV Local", "Google Sheets"])

    df = None

    if source == "CSV Local":
        uploaded_file = st.sidebar.file_uploader("Glissez votre fichier CSV ici", type="csv")
        
        if uploaded_file is not None:
            file_size_mo = uploaded_file.size / (1024 * 1024) # calcul de la taille du fichier en mégaoctet
            
            if file_size_mo > 200:
                st.sidebar.error(f"Le fichier est trop lourd ({file_size_mo:.1f} Mo). La limite est de 200 Mo.")
                df = None
            else:
                # Si le fichier est valide, on l'envoie à la fonction optimisée
                df = fetch_and_parse_data(uploaded_file)
                st.sidebar.success(f"Fichier chargé ({file_size_mo:.1f} Mo)")

    else:
        # Initialisation du session_state pour le bouton (effacer le lien)
        if 'gsheet_url' not in st.session_state:
            st.session_state.gsheet_url = ""

        def clear_url():
            st.session_state.gsheet_url = ""

        url = st.sidebar.text_input(
            "Collez l'URL de votre Google Sheet :", 
            key="gsheet_url"
        )
        
        # Petit bouton pour effacer le lien proprement
        st.sidebar.button("Effacer le lien", on_click=clear_url, type="secondary")

        if url:
            try:
                if "/edit" in url:
                    export_url = url.split('/edit')[0] + "/export?format=csv"
                    # section de l'url de google sheet et concatenation pour avoir un format csv
                    df = fetch_and_parse_data(export_url)
                else:
                    st.sidebar.error("L'URL semble incorrecte.")
            except Exception as e:
                st.sidebar.error(f"Erreur lors de la lecture : {e}")

    return df

def run_health_check(df):
    st.write("")
    st.markdown("<h1 style='color:green;'>Diagnostic de Santé des Données</h1>", unsafe_allow_html=True)
    
    # 1. Métriques de haut niveau et affichage
    st.markdown("<h3 style='color:cyan;'>Indicateurs Clés</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # Calculs
    total_cells = df.size
    total_missing = df.isnull().sum().sum()
    completeness = ((total_cells - total_missing) / total_cells) * 100

    # 100% : Le dataset est parfait, il n'y a aucun trou.
    # 90% : 1 cellule sur 10 est vide. C'est acceptable.

    # Nombre de colonnes ayant plus de 10% de vide
    #missing_pct_per_col = (df.isnull().sum() / len(df)) * 100
    #cols_at_risk = len(missing_pct_per_col[missing_pct_per_col > 10])
    #col5.metric("Colonnes à risque (>10%)", cols_at_risk)


    # Affichage
    col1.metric("Lignes", df.shape[0])
    col2.metric("Colonnes", df.shape[1])
    col3.metric("Doublons", df.duplicated().sum())
    col4.metric("Complétude", f"{completeness:.1f}%")

    if df.duplicated().sum() > 0:
        st.write(f":red[Attention : {df.duplicated().sum()} doublons détectés]")
    else:
        st.write(f":green[Aucun doublon]")

    if completeness >= 95.0:
        st.write(f":green[Complétude : {completeness:.1f}% Bonne complétude du fichier.]")
    elif 85 <= completeness < 95:
        st.write(f":orange[Complétude : {completeness:.1f}% : Acceptable, mais nécessite une investigation sur les colonnes vides.]")
    else:
        st.write(f":red[Complétude : {completeness:.1f}% : Critique. Nécéssite un nettoyage complet ou une revue du processus de collecte.]")

    # 2. Analyse des valeurs manquantes
    st.write("")
    st.write("")
    st.markdown("<h3 style='color:cyan;'>Taux de complétude</h3>", unsafe_allow_html=True)
    null_counts = df.isnull().sum() # calcul de chaque vide pour chaque colonne (True == vide == 1)
    null_pct = (null_counts / len(df)) * 100
    
    # Création d'un petit tableau récapitulatif
    health_df = pd.DataFrame({
        'Colonnes': df.columns,
        'Valeurs Manquantes': null_counts.values,
        'Pourcentage (%)': null_pct.values.round(2)
    }).sort_values(by='Pourcentage (%)', ascending=False) # affichage dans l'ordre décroisant en fonction des valeurs vides

    st.dataframe(health_df, use_container_width=True)

    # 3. Statistiques et Outliers
    st.write("")
    st.write("")
    st.markdown("<h3 style='color:cyan;'>Résumé Statistique sur les données du fichier</h3>", unsafe_allow_html=True)
    # On ne prend que les colonnes numériques pour les stats
    numeric_df = df.select_dtypes(include=['number'])
    
    if not numeric_df.empty:
        st.write(numeric_df.describe())
        
        # Détection d'outliers via IQR (Interquartile Range)
        st.markdown("<h3 style='color:cyan;'>Détection d'Outliers (IQR)</h3>", unsafe_allow_html=True)

        selected_col = st.selectbox("Sélectionner une colonne pour voir les outliers :", numeric_df.columns)
        
        Q1 = numeric_df[selected_col].quantile(0.25)
        Q3 = numeric_df[selected_col].quantile(0.75)
        IQR = Q3 - Q1   # le coeur des données, les données situées dans l’intervalle central de 50 %
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = numeric_df[(numeric_df[selected_col] < lower_bound) | (numeric_df[selected_col] > upper_bound)]
        
        if not outliers.empty:
            st.warning(f"Il y a {len(outliers)} outliers détectés pour {selected_col}.")
            st.write(outliers)
        else:
            st.success(f"Aucun outlier détecté pour {selected_col} !")
    else:
        st.info("Aucune donnée numérique détectée pour l'analyse statistique.")

def run_visualizations(df):
    st.markdown("<h1 style='color:green;'>Visualisation Interactive</h1>", unsafe_allow_html=True)

    # Onglets pour séparer les analyses
    tab1, tab2, tab3 = st.tabs(["Qualité de Remplissage","Distribution & Outliers",  "Corrélations"])

    with tab1:
        st.subheader("Qualité de remplissage")
        
        # Calcul du taux de présence par colonne
        completeness_per_col = (df.notnull().mean() * 100).reset_index()
        completeness_per_col.columns = ['Variable', 'Taux de Complétude (%)']
        completeness_per_col = completeness_per_col.sort_values(by='Taux de Complétude (%)')

        # Création du graphique à barres horizontales
        fig_comp = px.bar(completeness_per_col, 
                          x='Taux de Complétude (%)', 
                          y='Variable', 
                          orientation='h',
                          title="Fiabilité des données par colonne",
                          color='Taux de Complétude (%)',
                          color_continuous_scale='RdYlGn', # Rouge à Vert
                          range_x=[0, 100])

        # Ajout d'une ligne de seuil critique à 80%
        fig_comp.add_vline(x=80, line_dash="dash", line_color="red", 
                           annotation_text="Seuil critique (80%)")

        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.info("💡 Les colonnes à gauche de la ligne rouge sont jugées 'peu fiables' pour une analyse statistique sérieuse.")

    with tab2:
        st.subheader("Analyse de la Distribution")
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            col_to_plot = st.selectbox("Choisir une variable à visualiser :", numeric_cols, key="viz_dist")
            
            # Création d'un Boxplot + Histogramme combiné
            fig = px.histogram(df, x=col_to_plot, 
                               marginal="box", # Ajoute la boîte à moustaches au-dessus
                               title=f"Distribution de {col_to_plot}",
                               color_discrete_sequence=['#636EFA'])
            
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡Le 'Boxplot' au-dessus de l'histogramme montre visuellement les points isolés (outliers).")
        else:
            st.warning("Aucune donnée numérique disponible.")
    
    with tab3:
        st.subheader("Interdépendance des variables")
        
        numeric_df = df.select_dtypes(include=['number'])
        
        if numeric_df.shape[1] > 1:
            # Calcul de la matrice de corrélation (Pearson par défaut)
            corr_matrix = numeric_df.corr()

            # Création de la Heatmap Plotly
            fig_corr = px.imshow(corr_matrix,
                                 text_auto=".2f", # Affiche les valeurs dans les carrés
                                 aspect="auto",
                                 color_continuous_scale='RdBu_r', # Bleu (positif) à Rouge (négatif)
                                 range_color=[-1, 1],
                                 title="Matrice de corrélation de Pearson")
            
            st.plotly_chart(fig_corr, use_container_width=True)
            st.info("""
                💡 **Lecture du graphique :** * **1.0 (Rouge foncé) :** Corrélation parfaite (ex: une variable avec elle-même).  
                * **0 :** Aucune relation entre les deux variables.  
                * **-1.0 (Bleu foncé) :** Relation inverse (quand l'une monte, l'autre descend).
            """)
        else:
            st.warning("Il faut au moins deux colonnes numériques pour calculer des corrélations.")


if __name__ == "__main__":
    main()

    # Initialisation de l'application
    data = load_data()
    st.write("")
    st.write("")

    if data is not None:
        st.success("Données chargées avec succès !")
        st.write("Aperçu des données :", data.head())
    else:
        st.info("En attente de données...")

    # foncitons pour les stats globales du fichier

    if data is not None:
        run_health_check(data)
        st.write("")
        st.write("")
        st.write("")
        run_visualizations(data)



