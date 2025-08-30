import streamlit as st
import pandas as pd
import pymysql

# --------------------------
# DB Connection
# --------------------------
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="harvardartmuseums"
    )

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="Harvard’s Artifacts Collection", page_icon="🎨", layout="wide")
st.markdown("<h1 style='text-align:center;'>Harvard’s Artifacts Collection</h1>", unsafe_allow_html=True)

# --------------------------
# Initialize Session State
# --------------------------
if "inserted_classifications" not in st.session_state:
    st.session_state["inserted_classifications"] = []
if "selected_classification" not in st.session_state:
    st.session_state["selected_classification"] = None
if "df_meta" not in st.session_state:
    st.session_state["df_meta"] = None
    st.session_state["df_media"] = None
    st.session_state["df_colors"] = None
if "meta_json" not in st.session_state:
    st.session_state["meta_json"] = []
    st.session_state["media_json"] = []
    st.session_state["colors_json"] = []

# --------------------------
# Classification Selector
# --------------------------
options = ["Select Your Choice", "Paintings", "Sculpture", "Coins", "Drawings", "Vessels"]
classification = st.selectbox("Choose classification:", options, index=0)

if classification and classification != "Select Your Choice":
    st.session_state.selected_classification = classification

# --------------------------
# Collect Data Button
# --------------------------
if st.button("📥 Collect Data"):
    if classification == "Select Your Choice":
        st.warning("Please select a classification first ")
    else:
        st.success(f"✅ Data collected for classification: {classification}")

        conn = get_connection()

        df_meta = pd.read_sql(
            "SELECT * FROM artifact_metadata WHERE classification = %s LIMIT 2500",
            conn, params=[classification]
        )
        df_media = pd.read_sql(
            """
            SELECT m.* FROM artifact_media m
            JOIN artifact_metadata a ON m.objectid = a.id
            WHERE a.classification = %s LIMIT 2500
            """,
            conn, params=[classification]
        )
        df_colors = pd.read_sql(
            """
            SELECT c.* FROM artifact_colors c
            JOIN artifact_metadata a ON c.objectid = a.id
            WHERE a.classification = %s LIMIT 2500
            """,
            conn, params=[classification]
        )
        conn.close()

        # Save in session state
        st.session_state.df_meta = df_meta
        st.session_state.df_media = df_media
        st.session_state.df_colors = df_colors

        st.session_state.meta_json = df_meta.to_dict(orient="records")
        st.session_state.media_json = df_media.to_dict(orient="records")
        st.session_state.colors_json = df_colors.to_dict(orient="records")

# --------------------------
# SWIPE Navigation (Instead of Tabs)
# --------------------------
section = st.select_slider(
    "Navigate between sections",
    options=["Select Your Choice", "Migrate to SQL", "SQL Queries"],
    value="Select Your Choice"
)

# --- Section 1: JSON Preview ---
if section == "Select Your Choice":
    if st.session_state.meta_json:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("📑 Metadata")
            st.json(st.session_state.meta_json[:10])
        with col2:
            st.subheader("🖼️ Media")
            st.json(st.session_state.media_json[:10])
        with col3:
            st.subheader("🎨 Colors")
            st.json(st.session_state.colors_json[:10])
    else:
        st.info("No data collected yet. Select classification and click **Collect Data**.")

# --- Section 2: Insert to SQL ---
elif section == "Migrate to SQL":
    st.header("Insert Your Collected Data")

    selected_class = st.session_state.get("selected_classification", None)

    if st.button("Insert Data"):
        if not selected_class:
            st.error("⚠️ Please collect data first before inserting.")
        else:
            conn = get_connection()
            cursor = conn.cursor()

            if selected_class in st.session_state["inserted_classifications"]:
                st.error("Already inserted, please select another classification!")
            else:
                st.session_state["inserted_classifications"].append(selected_class)
                st.success(f"✅ Data inserted for {selected_class}!")

                all_classes = ", ".join([f"'{c}'" for c in st.session_state["inserted_classifications"]])
                if all_classes:
                    query_meta = f"SELECT * FROM artifact_metadata WHERE classification IN ({all_classes}) LIMIT 2500"
                    query_media = f"""
                        SELECT m.* FROM artifact_media m
                        JOIN artifact_metadata a ON m.objectid = a.id
                        WHERE a.classification IN ({all_classes}) LIMIT 2500
                    """
                    query_colors = f"""
                        SELECT c.* FROM artifact_colors c
                        JOIN artifact_metadata a ON c.objectid = a.id
                        WHERE a.classification IN ({all_classes}) LIMIT 2500
                    """

                    st.subheader("Artifact Metadata")
                    df1 = pd.read_sql(query_meta, conn)
                    st.dataframe(df1)

                    st.subheader("Artifact Media")
                    df2 = pd.read_sql(query_media, conn)
                    st.dataframe(df2)

                    st.subheader("Artifact Colors")
                    df3 = pd.read_sql(query_colors, conn)
                    st.dataframe(df3)

            conn.close()

# --- Section 3: Queries ---
elif section == "SQL Queries":
    st.subheader("Run Your SQL Query")

    queries = {
        "List all artifacts from the 11th century belonging to Byzantine culture":
            "SELECT * FROM artifact_metadata WHERE century = '11th century' AND culture = 'Byzantine'",
        "Unique cultures in artifacts":
            "SELECT DISTINCT culture FROM artifact_metadata WHERE culture IS NOT NULL",
        "List all artifacts from the Archaic Period":
            "SELECT * FROM artifact_metadata WHERE period = 'Archaic Period'",
        "Artifact titles ordered by accession year descending":
            "SELECT title, accessionyear FROM artifact_metadata WHERE accessionyear IS NOT NULL ORDER BY accessionyear DESC",
        "Artifacts per department":
            "SELECT department, COUNT(*) AS artifact_count FROM artifact_metadata GROUP BY department",
        "Artifacts with more than 1 media":
            "SELECT objectid FROM artifact_media GROUP BY objectid HAVING COUNT(*) > 1",
        "Average rank of artifacts":
            "SELECT AVG(rank) AS average_rank FROM artifact_media WHERE rank IS NOT NULL",
        "Artifacts with higher colorcount than mediacount":
            "SELECT m.objectid FROM artifact_media m JOIN artifact_metadata a ON m.objectid = a.id WHERE m.colorcount > m.mediacount",
        "Artifacts created between 1500 and 1600":
            "SELECT a.id, a.title, m.datebegin, m.dateend FROM artifact_metadata a JOIN artifact_media m ON a.id = m.objectid WHERE m.datebegin >= 1500 AND m.dateend <= 1600",
        "Artifacts with no media files":
            "SELECT COUNT(*) AS no_media_count FROM artifact_metadata a LEFT JOIN artifact_media m ON a.id = m.objectid WHERE m.objectid IS NULL",
        "Distinct hues":
            "SELECT DISTINCT hue FROM artifact_colors WHERE hue IS NOT NULL",
        "Top 5 most used colors":
            "SELECT color, COUNT(*) AS frequency FROM artifact_colors GROUP BY color ORDER BY frequency DESC LIMIT 5",
        "Average coverage per hue":
            "SELECT hue, AVG(coverage) AS avg_coverage FROM artifact_colors WHERE hue IS NOT NULL GROUP BY hue",
        "Colors for a specific artifact ID":
            "SELECT * FROM artifact_colors WHERE objectid = %s",
        "Total color entries":
            "SELECT COUNT(*) AS total_color_entries FROM artifact_colors",
        "Artifact titles and hues for Byzantine culture":
            "SELECT a.title, c.hue FROM artifact_metadata a JOIN artifact_colors c ON a.id = c.objectid WHERE a.culture = 'Byzantine'",
        "Each artifact title with its hues":
            "SELECT a.title, c.hue FROM artifact_metadata a LEFT JOIN artifact_colors c ON a.id = c.objectid WHERE c.hue IS NOT NULL",
        "Titles, cultures, media ranks where period not null":
            "SELECT a.title, a.culture, m.rank FROM artifact_metadata a JOIN artifact_media m ON a.id = m.objectid WHERE a.period IS NOT NULL",
        "Top 10 artifacts including hue 'Grey'":
            "SELECT a.title, m.rank FROM (SELECT objectid, rank FROM artifact_media ORDER BY rank ASC LIMIT 10) m JOIN artifact_metadata a ON m.objectid = a.id JOIN artifact_colors c ON a.id = c.objectid WHERE c.hue = 'Grey'",
        "Artifacts per classification and average media count":
            "SELECT a.classification, COUNT(*) AS artifact_count, AVG(m.mediacount) AS avg_media_count FROM artifact_metadata a LEFT JOIN artifact_media m ON a.id = m.objectid GROUP BY a.classification"
     # New Queries Added
        "List all artifacts from the 12th century belonging to Roman culture"
            "SELECT * FROM artifact_metadata WHERE century = '12th' AND culture = 'Roman'",
        "Unique periods represented in the dataset":
            "SELECT DISTINCT period FROM artifact_metadata",
        "List all artifacts from the Hellenistic Period":
            "SELECT * FROM artifact_metadata WHERE period = 'Hellenistic Period'",
        "Top 5 most used colors by frequency":
            "SELECT color, COUNT(*) AS freq FROM artifact_colors GROUP BY color ORDER BY freq DESC LIMIT 5",
        "Artifact titles, cultures, and media ranks where period is not null":
            "SELECT am.title, am.culture, med.rank FROM artifact_metadata am JOIN artifact_media med ON am.id = med.artifact_id WHERE am.period IS NOT NULL",
    }

    queries_list = ["-- Choose your query --"] + list(queries.keys())
    selected_query = st.selectbox("Select a Query", queries_list)

    if st.button("Run Query") and selected_query != "-- Choose your query --":
        conn = get_connection()
        cursor = conn.cursor()
        query = queries[selected_query]

        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=columns)

        st.subheader("Query Output")
        st.dataframe(df)

        cursor.close()
        conn.close()
