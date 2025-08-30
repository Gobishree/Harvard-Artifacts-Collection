import pymysql

def create_tables():
    # --- DB Connection ---
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="harvardartmuseums"   # DB name correct ah irukanum
    )
    cursor = conn.cursor()

    # --- Metadata table (12 columns) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifact_metadata (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255),
        culture VARCHAR(255),
        period VARCHAR(255),
        century VARCHAR(100),
        medium VARCHAR(255),
        dimensions VARCHAR(255),
        description TEXT,
        department VARCHAR(255),
        classification VARCHAR(255),
        accessionyear INT,
        accessionmethod VARCHAR(255)
    )
    """)

    # --- Media table (7 columns) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifact_media (
        media_id INT AUTO_INCREMENT PRIMARY KEY,
        objectid INT,
        imagecount INT,
        mediacount INT,
        colorcount INT,
        rank INT,
        datebegin INT,
        dateend INT,
        FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
    )
    """)

    # --- Colors table (6 columns) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifact_colors (
        color_id INT AUTO_INCREMENT PRIMARY KEY,
        objectid INT,
        color VARCHAR(50),
        spectrum VARCHAR(50),
        hue FLOAT,
        percent FLOAT,
        css3 VARCHAR(50),
        FOREIGN KEY (objectid) REFERENCES artifact_metadata(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Tables created successfully!")

# --- Run the function when script executes ---
if __name__ == "__main__":
    create_tables()
