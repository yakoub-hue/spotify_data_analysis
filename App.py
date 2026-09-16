import streamlit as st
import pandas as pd
import plotly.express as px
import kagglehub


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
    color: #1DB954;
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


# ============================================================
# 6. DONNÉES FILTRÉES POUR LA VUE GÉNÉRALE
# ============================================================

df_filtered = df.copy()


# Filtre genre

if genre_selectionne != "Tous les genres":

    df_filtered = df_filtered[
        df_filtered["track_genre"]
        == genre_selectionne
    ]


# Filtre popularité

df_filtered = df_filtered[
    df_filtered["popularity"]
    >= popularite_min
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


if df_filtered.empty:

    st.warning(
        "⚠️ Aucun titre ne correspond aux filtres sélectionnés."
    )

    st.stop()


# ============================================================
# 7. KPI
# ============================================================

popularite_moyenne = (
    df_filtered["popularity"].mean()
)

pourcentage_populaire = (
    (df_filtered["popularity"] > 50)
    .mean()
    * 100
)


# Genre le plus populaire sur le dataset filtré
# par popularité + contenu, mais sans filtre genre

df_kpi_genre = df.copy()

df_kpi_genre = df_kpi_genre[
    df_kpi_genre["popularity"]
    >= popularite_min
]

if explicit_filter == "Explicit":

    df_kpi_genre = df_kpi_genre[
        df_kpi_genre["explicit"] == True
    ]

elif explicit_filter == "Non explicit":

    df_kpi_genre = df_kpi_genre[
        df_kpi_genre["explicit"] == False
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

tab1, tab2, tab3 = st.tabs([
    "📊 Vue générale",
    "🎸 Comparer les genres",
    "🎚️ Caractéristiques audio"
])


# ============================================================
# ONGLET 1 : VUE GÉNÉRALE
# ============================================================

with tab1:

    st.subheader(
        "Comment se répartit la popularité des titres ?"
    )

    fig_pop = px.histogram(
        df_filtered,
        x="popularity",
        nbins=20
    )

    fig_pop.update_traces(
        marker_color="#1DB954"
    )

    fig_pop.update_layout(
        xaxis_title="Popularité (0 à 100)",
        yaxis_title="Nombre de titres",
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=480,
        bargap=0.03
    )

    fig_pop.update_xaxes(
        showgrid=False,
        range=[0, 100]
    )

    fig_pop.update_yaxes(
        gridcolor="#EEEEEE"
    )

    st.plotly_chart(
        fig_pop,
        use_container_width=True
    )


    # INTERPRÉTATION

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


    # IMPORTANT :
    # on repart du dataset complet
    # pour pouvoir comparer les genres

    df_genres = df.copy()


    # On garde le filtre popularité

    df_genres = df_genres[
        df_genres["popularity"]
        >= popularite_min
    ]


    # On garde le filtre Explicit

    if explicit_filter == "Explicit":

        df_genres = df_genres[
            df_genres["explicit"] == True
        ]

    elif explicit_filter == "Non explicit":

        df_genres = df_genres[
            df_genres["explicit"] == False
        ]


    # Statistiques par genre

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


    # Minimum 20 titres pour éviter
    # les comparaisons sur des échantillons minuscules

    genre_stats = genre_stats[
        genre_stats["nombre_titres"] >= 20
    ]


    # Top 10

    genre_stats = (
        genre_stats
        .sort_values(
            "popularite_moyenne",
            ascending=False
        )
        .head(10)
        .copy()
    )


    if genre_stats.empty:

        st.warning(
            "Pas assez de données pour comparer les genres "
            "avec les filtres actuels."
        )

    else:

        # Premier genre = vert
        # autres = gris

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


    # CORRÉLATION

    correlation = (
        df_filtered[
            [variable, "popularity"]
        ]
        .corr()
        .iloc[0, 1]
    )


    # Échantillon pour rendre
    # le graphique plus fluide

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


    # INTERPRÉTATION

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
            f"{correlation:.2f}"
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
# 10. CONCLUSION
# ============================================================

st.divider()

st.subheader("🎯 Conclusion")

st.markdown("""
<div class="message-box">

<strong>
Le succès d'un titre ne se résume pas à son profil audio.
</strong>

<br><br>

Le dashboard montre des différences de popularité entre
les genres. En revanche, les caractéristiques audio prises
individuellement présentent des relations limitées avec
la popularité.

<br><br>

Cela suggère que d'autres dimensions doivent également
être prises en compte pour comprendre le succès d'un titre.

</div>
""", unsafe_allow_html=True)