Harvard’s Artifacts Collection  
An interactive **Streamlit + MySQL project** to explore, migrate, and query the **Harvard Art Museums API dataset**.  
This project is designed for data extraction, transformation, and interactive visualization of cultural artifacts.
--> Features  

- **Collect Data**  
  - Choose from classifications (Paintings, Sculpture, Coins, Drawings, Vessels, etc.)  
  - Fetch data from database (previously loaded from Harvard Art Museums API)  
  - Preview results in **JSON format** before inserting  

- **Migrate to SQL**  
  - Insert collected data into MySQL database  
  - Automatically check if classification data is already inserted  
  - Display results in three tables:  
    - `artifact_metadata`  
    - `artifact_media`  
    - `artifact_colors`  

- **SQL Queries**  
  - Run pre-defined queries such as:  
    - Unique cultures  
    - Artifacts per department  
    - Top 5 most used colors  
    - Average coverage per hue  
  - Display results in a clean **dataframe format**  

--> Database Schema  

This project uses three main tables:

## 🗂️ Database Schema  

This project uses **3 SQL tables**:  

### `artifact_metadata`  (12 columns)  
| Column | Description |
|--------|-------------|
| id | Artifact ID |
| title | Artifact title |
| classification | Type (Painting, Sculpture, etc.) |
| culture | Culture associated |
| period | Period of creation |
| century | Century of artifact |
| department | Department of origin |
| accessionyear | Year of accession |
| accessionmethod | Method of acquisition |
| medium | Medium used |
| dimensions | Dimensions of artifact |
| description | Artifact description |

---

### `artifact_media`  (7 columns)  
| Column | Description |
|--------|-------------|
| objectid | Links to metadata.id |
| mediacount | Number of media files |
| rank | Rank of artifact |
| datebegin | Start year |
| dateend | End year |
| imageurl | Media image URL |
| technique | Media technique |

---

### `artifact_colors`  (6 columns)  
| Column | Description |
|--------|-------------|
| objectid | Links to metadata.id |
| color | Color name |
| hue | Hue group |
| saturation | Saturation value |
| lightness | Lightness value |
| coverage | Coverage percentage |

--> Tech Stack  
- **Python** (Streamlit, Pandas, PyMySQL)  
- **MySQL** for database management  
- **Harvard Art Museums API** (for original dataset extraction)  

-->How to Run  
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Harvard-Artifacts-Collection.git
   cd Harvard-Artifacts-Collection
