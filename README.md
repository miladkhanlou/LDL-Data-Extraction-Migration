# Extraction Phase in ETL Pipeline for Louisiana Digital Library (LDL)
### 1. PID Fetching:
We use a custom Drush command to fetch all Persistent Identifiers (PIDs) from a specific collection within the Islandora repository. These PIDs represent unique records or objects within the system.

### 2. Datastream Retrieval: 
After fetching the PIDs, the relevant datastreams (MODS, RELS-EXT, and OBJ) for each PID are extracted. These datastreams contain essential metadata (MODS), relational information (RELS-EXT), and binary objects (OBJ).

### 3. Compression and File Transfer: 
* All retrieved datastreams and binary files are compressed into a ZIP file for efficient transfer and storage.
* The ZIP file is securely transferred from the server to a local machine and then copied to an external storage location for further processing.

### 4. Decompression and Preparation: 
The compressed ZIP file is extracted into a designated directory, and any necessary file conversions (e.g., JP2 to PNG) are performed to ensure that the objects are in the correct format for the transformation phase.

---
# Transformation Phase in ETL Pipeline for Louisiana Digital Library (LDL)
The LDL Data Transformation Tools are designed for the Louisiana Digital Library (LDL) ETL pipeline, specifically to transform and clean metadata extracted from XML and RDF files. These tools prepare the data for ingestion into the new LDL website by converting XML and RDF formats into CSV files, which can then be used with Islandora Workbench for content migration. Below is an overview of two core tools involved in the transformation phase of the ETL pipeline.


## 1. XML to csv Scrip:
The xml to csv script is a Python tool designed to parse XML files, extract tags and attributes, check for errors, and convert the extracted data into CSV format for easy ingestion into Islandora. The script can operate in multiple modes depending on the task, from extracting unique tags to generating a Workbench-ready CSV.
### Features:

### 1-A) Extracting Unique Tags and Attributes
* The script processes a directory of XML files, identifying all unique tags and attributes.
* It counts the occurrences of each tag and attribute and exports this information into a CSV file.
* This process helps identify the structure of the XML data and prepares it for further analysis or ingestion.

#### Command Example: 
``python3 xml2csv.py -i INPUT_DIRECTORY -oat OUTPUT_DIRECTORY/OUTPUT_NAME.csv``

### 1-B) XML Path Error Detection and Frequency Analysis
* This mode reads through XML files to verify path consistency and check for spelling errors.
* It generates a CSV report containing unique XML paths and any errors detected during processing.

#### Command Example:
``python3 xml2csv.py -i INPUT_DIRECTORY -c MASTER_CSV -o OUTPUT_DIRECTORY/OUTPUT_NAME.csv``

### 1-C) XML to CSV Conversion:
* The script processes MODS XML files and converts them into a CSV format compatible with Islandora Workbench.
* It parses XML elements such as PIDs (Persistent Identifiers), tags, and attributes, mapping them to fields specified in a "Master CSV."
* This step ensures that metadata and content are properly formatted for ingestion into the Islandora repository.

#### Example of terminal command: 
`` python3 xml2csv.py -i FILE_DIRECTORY -cc MASTER_CSV -o OUTPUT_DIRECTORY/CSV_OUTPUT_NAME.csv `` </br></br>

### Command Example:
``python3 xml2csv.py -i INPUT_DIRECTORY -cc MASTER_CSV -o OUTPUT_DIRECTORY/OUTPUT_NAME.csv``
* **Important Notes on the Master CSV:**
* The Master CSV is an edited version of the output from the XML path extraction step. It contains field mappings (columns of field names associated with XPath).
* If a librarian needs to map an attribute’s value to a field, they must specify the XPath and indicate "yes" in the "att_needed" column.
* If only text values are required (and not attributes), the "att_needed" column should be left blank or set to "no."

## 2) Post-Processing Script:
The Post-Processing Script plays a crucial role in the final phase of metadata preparation for content migration. It processes RDF files and updates CSV files to ensure metadata is properly structured and formatted for ingestion into the Louisiana Digital Library (LDL) platform using Islandora Workbench. This script automates the task of refining metadata by adding necessary fields, validating file existence, and ensuring consistency across datasets.

### Features:
* RDF Metadata Processing: Parses RDF files to extract and update critical metadata fields such as collection relationships, resource types, and access terms.
* Metadata Enrichment: Adds fields like parent_id, field_weight, field_access_terms, and file paths to enhance the CSV file and ensure it meets the ingestion requirements for contet relationships for the new LDL platform.
* Data Cleaning: Removes unnecessary or redundant fields and ensures all required fields are properly structured for ingestion.

### Key Functionalities:
1. File Check and Metadata Updates:
  * The script verifies if all expected files exist in the dataset and updates the file column accordingly.
  * It maps access terms (related to collection or group associations) and fills in necessary metadata fields for Islandora Workbench.
2. RDF Parsing and Metadata Association:
  * Extracts metadata from RDF files to populate important fields such as parent-child relationships (parent_id), resource weights, and content types (e.g., "Image," "Paged Content," etc.).
3. Output Generation:
  * The processed data is saved into a final CSV file, ready for ingestion into Islandora Workbench.
### Command Example:
```python3 LDL-post-processing.py -c METADATA_CSV -f RDF_FILES_DIRECTORY -o OUTPUT_DIRECTORY/OUTPUT_NAME.csv```

### How These Tools Fit into the ETL Pipeline
These tools play a critical role in the Transformation phase of the ETL process for the Louisiana Digital Library. By automating the extraction and cleaning of metadata from XML and RDF files, they ensure that the content is correctly formatted for the Islandora repository, streamlining the content migration process.



