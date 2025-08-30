import requests
import pymysql
import pandas as pd
import math

# 🔑 Harvard API key
API_KEY = "be15f67b-1314-4f7d-8b20-5aae30d9feee"
url = "https://api.harvardartmuseums.org/object"
classifications = ["Paintings", "Sculpture","Coins","Drawings","Vessels"]

# ---- Helper to clean NaN for MySQL ----
def clean_value(val):
    if val is None: return None
    if isinstance(val, float) and math.isnan(val): return None
    return val

# ---- Fetch all records ----
all_records = []
for cls in classifications:
    print(f"🔎 Fetching {cls}...")
    for i in range(1, 26):  # 25 pages × 100 = 2500
        params = {"apikey": API_KEY,
                 "size": 100, 
                 "page": i, 
                 "classification": cls}
        data = requests.get(url, params).json()
        records = data.get("records", [])
        if not records: break
        all_records.extend(records)
        print(f"{cls} - Page {i}: {len(records)} records")

print(f"✅ Total records fetched: {len(all_records)}")

# ---- Convert JSON → DataFrames ----
metadata_df = pd.DataFrame([{
    "id": r.get("id"),
    "title": r.get("title"),
    "culture": r.get("culture"),
    "period": r.get("period"),
    "century": r.get("century"),
    "medium": r.get("medium"),
    "dimensions": r.get("dimensions"),
    "description": r.get("description"),
    "department": r.get("department"),
    "classification": r.get("classification"),
    "accessionyear": r.get("accessionyear"),
    "accessionmethod": r.get("accessionmethod"),
} for r in all_records])

media_df = pd.DataFrame([{
    "objectid": r.get("id"),
    "imagecount": r.get("imagecount"),
    "mediacount": r.get("mediacount"),
    "colorcount": r.get("colorcount"),
    "rank": r.get("rank"),
    "datebegin": r.get("datebegin"),
    "dateend": r.get("dateend")
} for r in all_records])

colors_df = pd.DataFrame([{
    "objectid": r.get("id"),
    "color": c.get("color"),
    "spectrum": c.get("spectrum"),
    "hue": c.get("hue"),
    "percent": c.get("percent"),
    "css3": c.get("css3")
} for r in all_records for c in (r.get("colors") or [])])

# ---- Insert into MySQL ----
conn = pymysql.connect(host="localhost", user="root", password="", database="harvardartmuseums")
cursor = conn.cursor()

# Metadata
cursor.executemany("""
    INSERT IGNORE INTO artifact_metadata
    (id, title, culture, period, century, medium, dimensions, description, department, classification, accessionyear, accessionmethod)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
""", [tuple(clean_value(row[col]) for col in metadata_df.columns) for _, row in metadata_df.iterrows()])

# Media
cursor.executemany("""
    INSERT IGNORE INTO artifact_media
    (objectid, imagecount, mediacount, colorcount, rank, datebegin, dateend)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
""", [tuple(clean_value(row[col]) for col in media_df.columns) for _, row in media_df.iterrows()])

# Colors
cursor.executemany("""
    INSERT IGNORE INTO artifact_colors
    (objectid, color, spectrum, hue, percent, css3)
    VALUES (%s,%s,%s,%s,%s,%s)
""", [tuple(clean_value(row[col]) for col in colors_df.columns) for _, row in colors_df.iterrows()])

conn.commit()
conn.close()

print(f"✅ Data inserted successfully! Metadata: {len(metadata_df)}, Media: {len(media_df)}, Colors: {len(colors_df)}")

