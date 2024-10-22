import pandas as pd
import xml.etree.ElementTree as ET
import glob
import os
import argparse

def process_command_line_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Post Processing for LDL Content Migration Using Islandora Workbench')
    parser.add_argument('-c', '--csv_directory', type=str, help='Path to metadata CSV', required=True)
    parser.add_argument('-f', '--files_directory', type=str, help='Path to RDF files', required=True)
    parser.add_argument('-o', '--output_directory', type=str, help='Path for output CSV', required=True)
    return parser.parse_args()

def load_metadata(csv_file):
    """Load metadata from CSV and return a DataFrame."""
    metadata_df = pd.read_csv(csv_file, encoding='utf-8')
    metadata_df.rename(columns={'PID': 'id'}, inplace=True)
    return metadata_df

def update_file_column(metadata_df, files_directory):
    """Update the 'file' column in the metadata DataFrame with file paths."""
    obj_names = ["{}_{}_OBJ".format(id.split(':')[0], id.split(':')[1])
                 for id in metadata_df["id"].tolist()]

    # Create a dictionary for file name lookup
    file_dict = {os.path.splitext(file)[0]: os.path.splitext(file)[1] 
                 for file in os.listdir(files_directory) if "OBJ" in file}

    metadata_df["file"] = [
        f"Data/{obj_name}{file_dict.get(obj_name, '')}" if obj_name in file_dict else ""
        for obj_name in obj_names
    ]

    return metadata_df

def map_access_terms(metadata_df):
    """Map collection keys to group names."""
    keys = ['amistad', 'apl', 'cppl', 'dcc', 'ebrpl', 'fpoc', 'hicks', 'hnoc',
            'lasc', 'lsm', 'lsu', 'lsua', 'lsus', 'lsuhsc', 'lsuhscs', 'latech',
            'loyno', 'louisiananewspapers', 'mcneese', 'nojh', 'nicholls', 'nsu',
            'oplib', 'slu', 'subr', 'sowela', 'tahil']
    
    values = ['Amistad', 'APL', 'CPPL', 'DCC', 'EBRPL', 'FPOC', 'Hicks', 'HNOC',
              'LASC', 'LSM', 'LSU', 'LSUA', 'LSUS', 'LSUHSC', 'LSUSHCS', 'LATECH',
              'LouisianaNewspapers', 'LOYNO', 'McNeese', 'NOJH', 'Nicholls', 'NSU',
              'OPLIB', 'SLU', 'SUBR', 'SOWELA', 'TAHIL']

    term_mapping = dict(zip(keys, values))
    metadata_df["field_access_terms"] = metadata_df["id"].apply(lambda x: term_mapping.get(x.split('-')[0], ''))
    
    return metadata_df

def parse_rdf_files(rdf_directory):
    """Parse RDF files and extract relevant metadata."""
    rdf_files = glob.glob(f"{rdf_directory}/*.rdf")
    rdf_files.sort()

    tags = []
    attributes = []
    text_values = []
    
    for rdf_file in rdf_files:
        try:
            tree = ET.parse(rdf_file)
            root = tree.getroot()
            
            for element in root.iter():
                tags.append(element.tag)
                attributes.append(element.attrib)
                text_values.append(element.text)
                
        except ET.ParseError as e:
            print(f"Error parsing {rdf_file}: {e}")
    
    return tags, attributes, text_values

def process_rdf_metadata(tags, attributes, text_values):
    """Extract and process data from RDF metadata."""
    tag_names = [tag.split('}')[-1] for tag in tags]
    
    weight_list = []
    content_type = []
    parent_ids = []
    viewers = []
    issue_dates = []
    
    for tag, attrib, text in zip(tag_names, attributes, text_values):
        if "isSequenceNumberOf" in tag:
            weight_list.append(text)
        else:
            weight_list.append("")
        
        # Determine content type and viewer based on model
        model = attrib.get('MODEL', '')
        if model == 'info:fedora/islandora:bookCModel':
            content_type.append('Paged Content')
            viewers.append('Mirador')
        elif model == 'info:fedora/islandora:sp_large_image_cmodel':
            content_type.append('Image')
            viewers.append('OpenSeadragon')
        elif model == 'info:fedora/islandora:sp_pdf':
            content_type.append('Document')
            viewers.append('PDF.js')
        else:
            content_type.append('')
            viewers.append('')

        # Extract date issued
        if "dateIssued" in tag and text:
            issue_dates.append(text)
        else:
            issue_dates.append('')
        
        # Extract parent ID
        if "isMemberOf" in tag and text:
            parent_ids.append(text.split('/')[-1])
        else:
            parent_ids.append('')
    
    return weight_list, content_type, viewers, parent_ids, issue_dates

def update_metadata_with_rdf(metadata_df, rdf_directory):
    """Update metadata DataFrame with data from RDF files."""
    tags, attributes, text_values = parse_rdf_files(rdf_directory)
    
    weight_list, content_type, viewers, parent_ids, issue_dates = process_rdf_metadata(tags, attributes, text_values)
    
    metadata_df["parent_id"] = parent_ids
    metadata_df["field_weight"] = weight_list
    metadata_df["field_model"] = content_type
    metadata_df["field_viewer_override"] = viewers
    metadata_df["field_edtf_date_issued"] = issue_dates
    metadata_df["field_edtf_date_created"] = ""
    metadata_df["field_linked_agent"] = ""

    # Sorting for better organization
    metadata_df.sort_values(by=['field_model', 'field_identifier', 'parent_id', 'field_weight'], 
                            ascending=[True, False, True, True], inplace=True)
    
    return metadata_df

def write_output(metadata_df, output_file):
    """Write the final processed metadata to a CSV file."""
    metadata_df.to_csv(output_file, index=False)
    print(f"Data successfully written to {output_file}")

def main():
    args = process_command_line_arguments()

    # Step 1: Load metadata from CSV
    metadata_df = load_metadata(args.csv_directory)

    # Step 2: Update file column based on available OBJ files
    metadata_df = update_file_column(metadata_df, args.files_directory)

    # Step 3: Map access terms
    metadata_df = map_access_terms(metadata_df)

    # Step 4: Update metadata with RDF data
    metadata_df = update_metadata_with_rdf(metadata_df, args.files_directory)

    # Step 5: Write the final CSV output
    write_output(metadata_df, args.output_directory)

if __name__ == "__main__":
    main()
