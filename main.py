import streamlit as st
import pandas as pd
import plotly.express as px
import kagglehub
import numpy as np


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Spotify - Analyse de popularité",
    page_icon="🎵",
    layout="wide"
)


# ============================================================
# 2. DESIGN
# ============================================================

st.markdown("""
<style>

:root {
    color-scheme: light;
}

.stApp {
    background-color: #F8F9FA;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1 {
    color: #191414 !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #191414 !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] {
    background-color: #F0F2F5;
    border-right: 1px solid #E5E7EB;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.05);
}

[data-testid="stMetricValue"] {
    color: #b91d34;
    font-size: 31px;
    font-weight: 700;
}

[data-testid="stMetricLabel"] {
    font-weight: 600;
}

.message-box {
    background-color: #EAF8EF;
    border-left: 5px solid #1DB954;
    padding: 17px 20px;
    border-radius: 8px;
    margin-top: 10px;
    margin-bottom: 25px;
}

.insight {
    background-color: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 16px;
    margin-top: 10px;
}

button[data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def load_data():

    path = kagglehub.dataset_download(
        "maharshipandya/-spotify-tracks-dataset"
    )

    df = pd.read_csv(
        path + "/dataset.csv",
        index_col=0
    )

    df = df.drop_duplicates().copy()

    for col in [
        "track_name",
        "artists",
        "album_name",
        "track_genre"
    ]:
        df[col] = df[col].fillna("Unknown")

    return df


df = load_data()


# ============================================================
# 4. TITRE
# ============================================================

st.title(
    "🎵 Qu'est-ce qui caractérise les titres populaires sur Spotify ?"
)

st.caption(
    "Dashboard interactif destiné à une équipe marketing musicale"
)

st.markdown("""
<div class="message-box">

<strong>💡 Message clé</strong><br><br>

Le genre musical permet d'observer des différences de popularité,
mais les caractéristiques audio prises individuellement
n'expliquent qu'une partie limitée du succès d'un titre.

</div>
""", unsafe_allow_html=True)


# ============================================================
# 5. FILTRES
# ============================================================

st.sidebar.header("🎛️ Filtres")

st.sidebar.caption(
    "Affinez l'analyse selon vos besoins."
)


# GENRE

genres = sorted(
    df["track_genre"]
    .dropna()
    .unique()
)

genre_selectionne = st.sidebar.selectbox(
    "🎸 Genre musical",
    options=["Tous les genres"] + genres
)


# POPULARITÉ

popularite_min = st.sidebar.slider(
    "⭐ Popularité minimum",
    min_value=0,
    max_value=100,
    value=0,
    help="0 permet d'afficher tous les titres."
)


# EXPLICIT

explicit_filter = st.sidebar.selectbox(
    "🔞 Type de contenu",
    [
        "Tous",
        "Explicit",
        "Non explicit"
    ]
)


# TEMPO

tempo_min_data = int(df["tempo"].min())
tempo_max_data = int(df["tempo"].max())

tempo_range = st.sidebar.slider(
    "🥁 Tempo (BPM)",
    min_value=tempo_min_data,
    max_value=tempo_max_data,
    value=(tempo_min_data, tempo_max_data),
    help="Filtre les titres selon leur tempo."
)


# RECHERCHE

recherche = st.sidebar.text_input(
    "🔍 Rechercher un titre ou un artiste",
    placeholder="Ex : Blinding Lights, Drake..."
)

st.sidebar.divider()

comparer_genres = st.sidebar.multiselect(
    "⚖️ Comparer des genres précis",
    options=genres,
    help="Choisissez 2 genres ou plus pour piloter "
         "la comparaison dans l'onglet « Comparer les genres »."
)


# ============================================================
# 6. DONNÉES FILTRÉES
# ============================================================

df_filtered = df.copy()


# Filtre genre

if genre_selectionne != "Tous les genres":

    df_filtered = df_filtered[
        df_filtered["track_genre"] == genre_selectionne
    ]


# Filtre popularité

df_filtered = df_filtered[
    df_filtered["popularity"] >= popularite_min
]


# Filtre contenu

if explicit_filter == "Explicit":

    df_filtered = df_filtered[
        df_filtered["explicit"] == True
    ]

elif explicit_filter == "Non explicit":

    df_filtered = df_filtered[
        df_filtered["explicit"] == False
    ]


# Filtre tempo

df_filtered = df_filtered[
    (df_filtered["tempo"] >= tempo_range[0])
    & (df_filtered["tempo"] <= tempo_range[1])
]


# Recherche titre / artiste

if recherche:

    masque_recherche = (
        df_filtered["track_name"].str.contains(
            recherche,
            case=False,
            na=False
        )
        |
        df_filtered["artists"].str.contains(
            recherche,
            case=False,
            na=False
        )
    )

    df_filtered = df_filtered[masque_recherche]


if df_filtered.empty:

    st.warning(
        "⚠️ Aucun titre ne correspond aux filtres sélectionnés."
    )

    st.stop()


# ============================================================
# 7. KPI
# ============================================================

popularite_moyenne = df_filtered["popularity"].mean()

pourcentage_populaire = (
    (df_filtered["popularity"] > 50).mean()
    * 100
)


# Calcul du genre en tête sans appliquer le filtre genre

df_kpi_genre = df.copy()

df_kpi_genre = df_kpi_genre[
    df_kpi_genre["popularity"] >= popularite_min
]


if explicit_filter == "Explicit":

    df_kpi_genre = df_kpi_genre[
        df_kpi_genre["explicit"] == True
    ]

elif explicit_filter == "Non explicit":

    df_kpi_genre = df_kpi_genre[
        df_kpi_genre["explicit"] == False
    ]


df_kpi_genre = df_kpi_genre[
    (df_kpi_genre["tempo"] >= tempo_range[0])
    & (df_kpi_genre["tempo"] <= tempo_range[1])
]


genre_kpi = (
    df_kpi_genre
    .groupby("track_genre")
    .agg(
        popularite_moyenne=("popularity", "mean"),
        nombre_titres=("track_id", "count")
    )
    .reset_index()
)


genre_kpi = genre_kpi[
    genre_kpi["nombre_titres"] >= 20
]


if not genre_kpi.empty:

    genre_top = (
        genre_kpi
        .sort_values(
            "popularite_moyenne",
            ascending=False
        )
        .iloc[0]["track_genre"]
    )

else:

    genre_top = "N/A"


# ============================================================
# 8. AFFICHAGE KPI
# ============================================================

st.subheader("📌 En un coup d'œil")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "⭐ Popularité moyenne",
        f"{popularite_moyenne:.1f}/100"
    )


with col2:

    st.metric(
        "🔥 Titres populaires (> 50)",
        f"{pourcentage_populaire:.1f}%"
    )


with col3:

    if genre_selectionne == "Tous les genres":

        st.metric(
            "🏆 Genre en tête",
            genre_top
        )

    else:

        st.metric(
            "🎸 Genre analysé",
            genre_selectionne
        )


st.caption(
    f"📚 {len(df_filtered):,} titres analysés "
    "avec les filtres actuels."
)

st.divider()


# ============================================================
# 9. ONGLETS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue générale",
    "🎸 Comparer les genres",
    "🎚️ Caractéristiques audio",
    "🔍 Explorer les titres"
])


# ============================================================
# ONGLET 1 : VUE GÉNÉRALE
# ============================================================

with tab1:

    st.subheader(
        "Comment se répartit la popularité des titres ?"
    )

    # Création de 10 tranches de popularité
    counts, bins = np.histogram(
        df_filtered["popularity"],
        bins=10,
        range=(0, 100)
    )

    hist_df = pd.DataFrame({
        "debut": bins[:-1],
        "fin": bins[1:],
        "nombre": counts
    })

    # Nom des tranches
    hist_df["intervalle"] = hist_df.apply(
        lambda x: (
            f"{int(x['debut'])}-{int(x['fin'])}"
        ),
        axis=1
    )

    # Identification du minimum et du maximum
    min_index = hist_df["nombre"].idxmin()
    max_index = hist_df["nombre"].idxmax()

    # Toutes les barres sont grises au départ
    hist_df["niveau"] = "Autres"

    # Minimum = rouge
    hist_df.loc[min_index, "niveau"] = "Minimum"

    # Maximum = vert
    hist_df.loc[max_index, "niveau"] = "Maximum"

    # Graphique
    fig_pop = px.bar(
        hist_df,
        x="intervalle",
        y="nombre",
        color="niveau",
        color_discrete_map={
            "Maximum": "#1DB954",
            "Minimum": "#EF4444",
            "Autres": "#D1D5DB"
        },
        labels={
            "intervalle": "Popularité",
            "nombre": "Nombre de titres",
            "niveau": ""
        },
        hover_data={
            "debut": False,
            "fin": False,
            "niveau": False
        }
    )

    fig_pop.update_layout(
        xaxis_title="Popularité (0 à 100)",
        yaxis_title="Nombre de titres",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=500,
        bargap=0.03,
        legend_title_text=""
    )

    fig_pop.update_xaxes(
        showgrid=False
    )

    fig_pop.update_yaxes(
        gridcolor="#EEEEEE"
    )

    st.plotly_chart(
        fig_pop,
        use_container_width=True
    )


    # Informations min / max

    col_max, col_min = st.columns(2)

    with col_max:

        st.success(
            f"🟢 **Maximum : {hist_df.loc[max_index, 'intervalle']}**  \n"
            f"{hist_df.loc[max_index, 'nombre']:,} titres"
        )

    with col_min:

        st.error(
            f"🔴 **Minimum : {hist_df.loc[min_index, 'intervalle']}**  \n"
            f"{hist_df.loc[min_index, 'nombre']:,} titres"
        )


    # Interprétation

    if popularite_moyenne < 30:

        interpretation = (
            "Les titres sélectionnés ont globalement "
            "une popularité plutôt faible."
        )

    elif popularite_moyenne < 60:

        interpretation = (
            "Les titres sélectionnés ont globalement "
            "une popularité intermédiaire."
        )

    else:

        interpretation = (
            "Les titres sélectionnés ont globalement "
            "une popularité élevée."
        )


    st.markdown(
        f"""
        <div class="insight">

        <strong>💡 À retenir</strong><br><br>

        {interpretation}

        La popularité moyenne est de
        <strong>{popularite_moyenne:.1f}/100</strong>.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# ONGLET 2 : COMPARAISON DES GENRES
# ============================================================

with tab2:

    st.subheader(
        "Quels genres ont la popularité moyenne la plus élevée ?"
    )

    st.caption(
        "Cette vue compare tous les genres. "
        "Le filtre « Genre musical » n'est pas appliqué ici."
    )


    df_genres = df.copy()


    # Popularité

    df_genres = df_genres[
        df_genres["popularity"] >= popularite_min
    ]


    # Explicit

    if explicit_filter == "Explicit":

        df_genres = df_genres[
            df_genres["explicit"] == True
        ]

    elif explicit_filter == "Non explicit":

        df_genres = df_genres[
            df_genres["explicit"] == False
        ]


    # Tempo

    df_genres = df_genres[
        (df_genres["tempo"] >= tempo_range[0])
        & (df_genres["tempo"] <= tempo_range[1])
    ]


    # Statistiques

    genre_stats = (
        df_genres
        .groupby("track_genre")
        .agg(
            popularite_moyenne=(
                "popularity",
                "mean"
            ),
            nombre_titres=(
                "track_id",
                "count"
            )
        )
        .reset_index()
    )


    genre_stats = genre_stats[
        genre_stats["nombre_titres"] >= 20
    ]


    # Comparaison manuelle ou Top 10

    if comparer_genres:

        genre_stats = (
            genre_stats[
                genre_stats["track_genre"].isin(
                    comparer_genres
                )
            ]
            .sort_values(
                "popularite_moyenne",
                ascending=False
            )
            .copy()
        )

        titre_top10 = (
            "🎯 Comparaison des genres sélectionnés"
        )

    else:

        genre_stats = (
            genre_stats
            .sort_values(
                "popularite_moyenne",
                ascending=False
            )
            .head(10)
            .copy()
        )

        titre_top10 = "🔟 Top 10 des genres"


    st.caption(titre_top10)


    if genre_stats.empty:

        st.warning(
            "Pas assez de données pour comparer "
            "les genres avec les filtres actuels."
        )

    else:

        genre_stats["groupe"] = "Autres genres"

        genre_stats.iloc[
            0,
            genre_stats.columns.get_loc("groupe")
        ] = "Genre en tête"


        fig_genre = px.bar(
            genre_stats,
            x="popularite_moyenne",
            y="track_genre",
            orientation="h",
            color="groupe",
            color_discrete_map={
                "Genre en tête": "#1DB954",
                "Autres genres": "#D8DDE3"
            },
            hover_data={
                "nombre_titres": True,
                "groupe": False
            },
            labels={
                "popularite_moyenne":
                    "Popularité moyenne",
                "track_genre":
                    "Genre",
                "nombre_titres":
                    "Nombre de titres"
            }
        )


        fig_genre.update_layout(
            xaxis_title="Popularité moyenne",
            yaxis_title="",
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=500,
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )


        fig_genre.update_xaxes(
            gridcolor="#EEEEEE",
            range=[0, 100]
        )

        fig_genre.update_yaxes(
            showgrid=False
        )


        st.plotly_chart(
            fig_genre,
            use_container_width=True
        )


        top = genre_stats.iloc[0]


        st.markdown(
            f"""
            <div class="insight">

            <strong>🎯 À retenir</strong><br><br>

            Avec les filtres actuels,
            <strong>{top["track_genre"]}</strong>
            possède la popularité moyenne la plus élevée
            parmi les genres comparés :

            <strong>
            {top["popularite_moyenne"]:.1f}/100
            </strong>.

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ONGLET 3 : CARACTÉRISTIQUES AUDIO
# ============================================================

with tab3:

    st.subheader(
        "Les caractéristiques audio sont-elles liées à la popularité ?"
    )


    variables_audio = {

        "Dansabilité":
            "danceability",

        "Énergie":
            "energy",

        "Positivité":
            "valence",

        "Acoustique":
            "acousticness",

        "Présence de paroles":
            "speechiness",

        "Son live":
            "liveness",

        "Instrumental":
            "instrumentalness",

        "Volume sonore":
            "loudness",

        "Tempo":
            "tempo"
    }


    variable_nom = st.selectbox(
        "🎚️ Caractéristique à analyser",
        list(variables_audio.keys())
    )


    variable = variables_audio[
        variable_nom
    ]


    afficher_tendance = st.checkbox(
        "📈 Afficher la droite de tendance",
        value=False
    )


    # Corrélation

    correlation = (
        df_filtered[
            [variable, "popularity"]
        ]
        .corr()
        .iloc[0, 1]
    )


    # Échantillon pour la fluidité

    if len(df_filtered) > 4000:

        df_graph = df_filtered.sample(
            4000,
            random_state=42
        )

    else:

        df_graph = df_filtered


    fig_audio = px.scatter(
        df_graph,
        x=variable,
        y="popularity",
        hover_data=[
            "track_name",
            "artists",
            "track_genre"
        ],
        opacity=0.30,
        trendline=(
            "ols"
            if afficher_tendance
            else None
        ),
        trendline_color_override="#191414",
        labels={
            variable: variable_nom,
            "popularity": "Popularité"
        }
    )


    fig_audio.update_traces(
        marker=dict(
            color="#1DB954",
            size=6
        )
    )


    fig_audio.update_layout(
        xaxis_title=variable_nom,
        yaxis_title="Popularité (0 à 100)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=480
    )


    fig_audio.update_xaxes(
        gridcolor="#EEEEEE"
    )

    fig_audio.update_yaxes(
        gridcolor="#EEEEEE",
        range=[0, 100]
    )


    st.plotly_chart(
        fig_audio,
        use_container_width=True
    )


    # Interprétation corrélation

    if pd.isna(correlation):

        force_relation = "non calculable"
        correlation_affichage = "N/A"

    else:

        correlation_affichage = f"{correlation:.2f}"

        if abs(correlation) < 0.10:

            force_relation = "très faible"

        elif abs(correlation) < 0.30:

            force_relation = "faible"

        elif abs(correlation) < 0.50:

            force_relation = "modérée"

        else:

            force_relation = "forte"


    col_a, col_b = st.columns(
        [1, 2]
    )


    with col_a:

        st.metric(
            "🔗 Corrélation",
            correlation_affichage
        )


    with col_b:

        st.markdown(
            f"""
            <div class="insight">

            <strong>💡 Comment lire le résultat ?</strong>
            <br><br>

            La relation entre
            <strong>{variable_nom.lower()}</strong>
            et la popularité est
            <strong>{force_relation}</strong>.

            <br><br>

            Plus la corrélation est proche de 0,
            moins cette caractéristique est liée,
            à elle seule, à la popularité.

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ONGLET 4 : EXPLORER LES TITRES
# ============================================================

with tab4:

    st.subheader(
        "Parcourir et trier les titres filtrés"
    )

    st.caption(
        "Cliquez sur l'en-tête d'une colonne pour trier. "
        "Utilisez la recherche et les filtres de la sidebar "
        "pour réduire la liste."
    )


    colonnes_a_afficher = [
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "danceability",
        "energy",
        "tempo",
        "explicit"
    ]


    tri_par = st.selectbox(
        "Trier par",
        colonnes_a_afficher,
        index=colonnes_a_afficher.index(
            "popularity"
        )
    )


    ordre_desc = st.toggle(
        "Ordre décroissant",
        value=True
    )


    df_table = (
        df_filtered[
            colonnes_a_afficher
        ]
        .sort_values(
            tri_par,
            ascending=not ordre_desc
        )
    )


    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True,
        height=430
    )


    st.download_button(
        "⬇️ Télécharger cette sélection (CSV)",
        data=df_table.to_csv(
            index=False
        ).encode("utf-8"),
        file_name="titres_filtres.csv",
        mime="text/csv"
    )


# ============================================================
# 10. CONCLUSION
# ============================================================

st.divider()

st.subheader("🎯 Conclusion")

st.markdown("""
<div class="message-box">

<strong>
Le succès d'un titre ne se résume pas à son profil audio.
Le dashboard montre des différences de popularité entre
les genres. En revanche, les caractéristiques audio prises
individuellement présentent des relations limitées avec
la popularité.
Cela suggère que d'autres dimensions doivent également
être prises en compte pour comprendre le succès d'un titre.
</strong>
</div>
""", unsafe_allow_html=True)