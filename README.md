# LDL Data Transformation tools:
The LDL Data Transformation Tools are designed for the Louisiana Digital Library (LDL) ETL pipeline, specifically to transform and clean metadata extracted from XML and RDF files. These tools prepare the data for ingestion into the new LDL website by converting XML and RDF formats into CSV files, which can then be used with Islandora Workbench for content migration. Below is an overview of two core tools involved in the transformation phase of the ETL pipeline.


## 1. XML to csv Scrip:
The XML2Workbench script is a Python tool designed to parse XML files, extract tags and attributes, check for errors, and convert the extracted data into CSV format for easy ingestion into Islandora. The script can operate in multiple modes depending on the task, from extracting unique tags to generating a Workbench-ready CSV.
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
The LDL Post-Processing script is designed for the final phase of metadata preparation, where RDF files are processed to update and refine CSV files for content migration. It ensures that metadata is correctly structured for ingestion into the new LDL platform using Islandora Workbench.
### Features:
* Processes metadata from RDF files and extracts key information, such as collection relationships, resource types, and access terms.
* Updates the CSV with additional fields such as parent_id, field_weight, field_access_terms, and file_paths.
* Removes unnecessary fields from the metadata and ensures that all required fields are properly formatted for ingestion.
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

---
# LSU ETL Pipeline:
## Data Extraction:
### 1. Extract data Using drush
- collection_name:collection
```sh
cd /var/www/drupal7

drush -u 1 islandora_datastream_crud_fetch_pids --namespace=collection_name --pid_file=/tmp/collection_name.txt

drush -u 1 idcrudfd --pid_file=/tmp/collection_name.txt --datastreams_directory=/tmp/collection_name --dsid=MODS
drush -u 1 idcrudfd --pid_file=/tmp/collection_name.txt --datastreams_directory=/tmp/collection_name --dsid=RELS-EXT
drush -u 1 idcrudfd --pid_file=/tmp/collection_name.txt --datastreams_directory=/tmp/collection_name --dsid=OBJ
```
### 2. Place Extracted data
```sh
cd /tmp/collection_name
zip collection_name.zip *
ctl-D
ctl-D
```
### 3. Copy to the target location:
```sh
scp dgi-ingest:/tmp/collection_name/amistad-pgoudvis.zip ~/Downloads
cp ~/Downloads/collection_name.zip /meda/wwc/0A2C-888E/collection_name/

cd /media/wwc/0A2C-888E/collection_name
mkdir Data
cd Data
unzip ../collection_name.zip 

for f in *.jp2; do opj_decompress -i "$f" -OutFor PNG -o "${f%.*}.png"; done;
```

## Data Transformation using xml2csv python script:
### STEP1: get the attribute and tags:
- For windows: ```python3 '.\xml2csv_2.py' -i DATA_DIR -oat OUTPUT_DIR/CSV_NAME(no.csv)```

### STEP2: get paths and errors: 
- For windows: ```python3 '.\xml2csv.py' -i DATA_DIR -c STEP1_csv(NAME.CSV) v -o OUTPUT_DIR/CSV_NAME(no.csv)```

### STEP3: run xml to csv using the csv field mapping:
- For windows: ```python3 '.\xml2csv.py' -i DATA_DIR -cc MAPPED_CSV -o OUTPUT_DIR/CSV_NAME(no.csv)```


## Data Ingestion using Workbench tool :
```sh
./workbench --config CONFIG.yml --check
./workbench --config CONFIG.yml 
```

***************
### Functions
The code is organized into several functions: </br>
a.	process_command_line_arguments():</br>
This function processes command-line arguments using the argparse library and returns the parsed arguments as an object.</br></br>
b.	files_directories(all_files):</br>
This function takes a directory path and returns a list of file paths in that directory.</br></br>
c.	csv_directories(metadata_csv):</br>
This function takes a directory path and returns a list of CSV files in that directory.</br></br>
d.	objects_to_df(csvs, OBJS)</br>

***************

### Command Line Arguments
The code uses command-line arguments to specify the input and output directories and the CSV file with metadata.)</br>
Command Line Arguments:)</br>
-c or --csv_directory: Path to the directory containing CSV files with metadata.)</br>
-f or --files_directory: Path to the directory containing object files (OBJs).)</br>
-o or --output_directory: Path to the directory where the output CSV files will be saved.)</br>






