import xml.etree.ElementTree as ET
import csv
from os import listdir
import re
import pandas as pd
import argparse
import datetime

# Global variables
paths_counts = {}
unique_tags = {}
unique_attributes = {}

start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def process_command_line_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Process XML files and extract tags/attributes.')
    parser.add_argument('-i', '--input_directory', type=str, help='Path to the input directory', required=True)
    parser.add_argument('-oat', '--output_attribsTags', type=str, help='Output CSV for attributes/tags', required=False)
    parser.add_argument('-c', '--input_csv', type=str, help='Path to input CSV', required=False)
    parser.add_argument('-cc', '--input_clear_csv', type=str, help='Path to cleared CSV', required=False)
    parser.add_argument('-o', '--output_directory', type=str, help='Path for output CSV containing results', required=False)
    return parser.parse_args()

def process_xml_files(directory):
    """Process XML files in the given directory."""
    files = listdir(directory)
    for file in sorted(files):
        if file.endswith(".xml"):
            file_path = f"{directory}/{file}"
            print(f"Parsing {file}...")
            yield ET.iterparse(file_path, events=('start', 'end'))

def extract_unique_tags_and_attributes(tags, attributes):
    """Count occurrences of unique tags and attributes."""
    for tag in tags:
        unique_tags[tag] = unique_tags.get(tag, 0) + 1
    
    for attribute in attributes:
        unique_attributes[attribute] = unique_attributes.get(attribute, 0) + 1

def save_data_to_csv(args, tag_data, attribute_data):
    """Save extracted tag and attribute data to CSV."""
    data = {'tags': [], 'tags_frequency': [], 'attributes': [], 'attributes_frequency': []}

    for tag, count in tag_data.items():
        data['tags'].append(tag)
        data['tags_frequency'].append(count)

    for attribute, count in attribute_data.items():
        data['attributes'].append(attribute)
        data['attributes_frequency'].append(count)

    df = pd.DataFrame(data)
    df.to_csv(args.output_attribsTags, index=False)
    print(f"Data saved to {args.output_attribsTags}")

def generate_workbench_csv(args, dataframe):
    """Convert XML data to a format compatible with Islandora Workbench."""
    for root in process_xml_files(args.input_directory):
        process_xml_data(root, dataframe)

def process_xml_data(root, dataframe):
    """Parse XML file and extract paths, tags, attributes, and values."""
    all_paths = []
    result_dict = {}

    for event, elem in root:
        tag_name = elem.tag.split("}")[-1]
        attributes = elem.attrib
        
        # Handle attributes
        if attributes:
            paths = [f"{tag_name}[@{k}='{v}']" for k, v in attributes.items()]
        else:
            paths = [tag_name]

        # Collect paths and values
        if event == 'start':
            all_paths.extend(paths)

        # Finalize XML paths and extract text
        if event == 'end' and elem.text and elem.text.strip():
            result_dict['/'.join(all_paths)] = elem.text.strip()
            all_paths.pop()

    return result_dict

def main():
    args = process_command_line_arguments()
    
    if args.output_attribsTags:
        unique_tags.clear()
        unique_attributes.clear()
        for root in process_xml_files(args.input_directory):
            tags, attributes = [], []
            for _, elem in root:
                tags.append(elem.tag.split("}")[-1])
                attributes.extend(elem.attrib.keys())
            extract_unique_tags_and_attributes(tags, attributes)
        save_data_to_csv(args, unique_tags, unique_attributes)

    if args.input_csv and args.output_directory:
        dataframe = pd.read_csv(args.input_csv)
        generate_workbench_csv(args, dataframe)

if __name__ == "__main__":
    main()
