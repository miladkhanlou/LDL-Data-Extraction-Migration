import xml.etree.ElementTree as ET
import csv
import os
from itertools import combinations
from os import listdir
import re
import pandas as pd
import argparse
import datetime
import numpy as np

# =======================================
# Command-Line Argument Parsing
# =======================================
def process_command_line_arguments():
    parser = argparse.ArgumentParser(description='Attribute and Tag Finder for XML Collections')
    parser.add_argument('-i', '--input_directory', type=str, help='Path to the input directory')
    parser.add_argument('-oat', '--output_attribsTags', type=str, help='Path to the output attributes and tags file')
    parser.add_argument('-c', '--attribute_tag_csv', type=str, help='Path to the attribute-tag input CSV file')
    parser.add_argument('-cc', '--mapping_csv', type=str, help='Path to the mapping input CSV file')
    parser.add_argument('-o', '--output_directory', type=str, help='Path to the output CSV')
    parser.add_argument('-ow', '--output_directory_w', type=str, help='Path to the writable output CSV')
    return parser.parse_args()

# =======================================
# Utility Functions
# =======================================
def read_csv(file_path, is_mapping=False):
    df = pd.read_csv(file_path)
    if is_mapping:
        df = df[df['needed'] == 'yes']
        df['att_needed'] = df['att_needed'].fillna("no").str.strip().str.lower()
    return df

def generate_attribute_permutations(attributes):
    keys = list(attributes.keys())
    permutations = []
    for r in range(1, len(keys) + 1):
        for combo in combinations(keys, r):
            permutation = {k: attributes[k] for k in combo}
            permutations.append(permutation)
    return permutations

# =======================================
# Main XML Parsing Logic
# =======================================
def parse_xml_file(file_path, arg, mapping_df=None):
    print(f"Parsing {os.path.basename(file_path)} ...")
    root = ET.iterparse(file_path, events=('start', 'end'))
    all_tags, all_attribs, path_list, mapped_data = [], [], [], {}

    path_stack = []
    for event, elem in root:
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if event == 'start':
            path_stack.append(tag)
            current_path = '/'.join(path_stack)
            
            if arg.attribute_tag_csv:
                path_list.append(current_path)

            if arg.mapping_csv and current_path not in mapped_data:
                mapped_data[current_path] = elem.text.strip() if elem.text else ""
            
            if elem.attrib:
                attributes = elem.attrib
                combined_attrs = ", ".join(sorted(f"@{k.split('}')[-1]}='{v}'" for k, v in attributes.items()))
                combined_path = f"{current_path} [{combined_attrs}]"

                if arg.attribute_tag_csv:
                    path_list.append(combined_path)

                if arg.mapping_csv and combined_path not in mapped_data:
                    mapped_data[combined_path] = elem.text.strip() if elem.text else ""

                for attrib in attributes.items():
                    all_attribs.append(attrib)

                for perm in generate_attribute_permutations(attributes):
                    perm_attrs = ", ".join(f"@{k.split('}')[-1]}='{v}'" for k, v in perm.items())
                    perm_path = f"{current_path} [{perm_attrs}]"

                    if arg.attribute_tag_csv:
                        path_list.append(perm_path)

        elif event == 'end':
            path_stack.pop()
            elem.clear()

    if arg.attribute_tag_csv:
        return path_list

    if arg.mapping_csv:
        return map_to_fields(file_path, mapped_data, mapping_df)

    return all_attribs, all_tags

def map_to_fields(filename, xml_data, mapping_df):
    pid = extract_pid(filename)
    mapped_data = {"pid": pid}

    for path in mapping_df["xpaths"]:
        field_name = mapping_df.loc[mapping_df['xpaths'] == path, 'fields'].values[0]
        value = xml_data.get(path, "").strip()
        
        if field_name in mapped_data and mapped_data[field_name]:
            mapped_data[field_name] = f"{mapped_data[field_name]} -- {value}" if value else mapped_data[field_name]
        else:
            mapped_data[field_name] = value

    return mapped_data

def extract_pid(file_name):
    match = re.search(r'[^/]+(?=_MODS)', file_name)
    return match.group(0).replace('_', ':') if match else ""

# =======================================
# Output Writing
# =======================================
def write_to_csv(data, output_file):
    start_time = datetime.datetime.now()
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    end_time = datetime.datetime.now()
    print(f"Output written to {output_file}")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

# =======================================
# Main Function
# =======================================
def main():
    args = process_command_line_arguments()

    if args.input_directory and args.output_attribsTags:
        all_attribs_tags = []
        for file in sorted(listdir(args.input_directory)):
            if file.endswith(".xml"):
                file_path = os.path.join(args.input_directory, file)
                attribs_tags = parse_xml_file(file_path, args)
                all_attribs_tags.extend(attribs_tags)

        write_to_csv(all_attribs_tags, args.output_attribsTags)

    elif args.input_directory and args.output_directory and args.attribute_tag_csv:
        attribute_data = []
        for file in sorted(listdir(args.input_directory)):
            if file.endswith(".xml"):
                file_path = os.path.join(args.input_directory, file)
                paths = parse_xml_file(file_path, args)
                attribute_data.extend(paths)

        write_to_csv(attribute_data, args.output_directory)

    elif args.mapping_csv and args.input_directory and args.output_directory:
        mapping_df = read_csv(args.mapping_csv, is_mapping=True)
        mapped_data = []

        for file in sorted(listdir(args.input_directory)):
            if file.endswith(".xml"):
                file_path = os.path.join(args.input_directory, file)
                mapped_result = parse_xml_file(file_path, args, mapping_df)
                mapped_data.append(mapped_result)

        write_to_csv(mapped_data, args.output_directory)

if __name__ == "__main__":
    main()
