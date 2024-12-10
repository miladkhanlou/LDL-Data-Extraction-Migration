import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os
import re
import numpy as np
from itertools import combinations

# ----------------------------------------------------------------------
# PART I: Command Line Argument Parser
# ----------------------------------------------------------------------
def process_command_line_arguments():
    parser = argparse.ArgumentParser(description="Attribute and Tag Finder for XML Collections")
    parser.add_argument('-i', '--input_directory', type=str, help='Path to the input directory', required=False)
    parser.add_argument('-oat', '--output_attribsTags', type=str, help='Path to the output attribute and tag list text file', required=False)
    parser.add_argument('-c', '--attribute_tag_csv', type=str, help='Path to the input CSV file', required=False)
    parser.add_argument('-cc', '--mapping_csv', type=str, help='Path to the mapping CSV file', required=False)
    parser.add_argument('-o', '--output_directory', type=str, help='Path to the output CSV file', required=False)
    return parser.parse_args()

# ----------------------------------------------------------------------
# PART II: Helper Functions
# ----------------------------------------------------------------------
def get_csv(csv_file, args):
    """Load the CSV file and return relevant data based on the mode."""
    df = pd.read_csv(csv_file)
    if args.mapping_csv:
        mapping_df = df[df['needed'] == 'yes']
        mapping_df['att_needed'] = mapping_df['att_needed'].fillna("no").str.strip().str.lower()
        return mapping_df
    elif args.attribute_tag_csv:
        return {col: list(df[col]) for col in df.columns}

def get_pid(file_name):
    """Extract and format the PID from the file name."""
    match = re.search(r'[^/]+(?=_MODS)', file_name)
    return match.group(0).replace('_', ':') if match else ""

# ----------------------------------------------------------------------
# PART III: XML Parsing Functions
# ----------------------------------------------------------------------
def initiate_parse(input_dir, args, mapping_df=None):
    """Parse XML files in the input directory based on the selected mode."""
    files = sorted(f for f in os.listdir(input_dir) if f.endswith(".xml"))
    all_attribs, all_tags, all_paths, combined_dict = {}, {}, {}, []

    for file in files:
        file_path = os.path.join(input_dir, file)
        root = ET.iterparse(file_path, events=('start', 'end'))
        print(f"\nParsing {file} ...")

        if args.mapping_csv:
            result = xml_parse(root, file, args, mapping_df)
            combined_dict.append(result)
        elif args.attribute_tag_csv:
            result = xml_parse(root, file, args)
            for xpath in result:
                all_paths[xpath] = all_paths.get(xpath, 0) + 1
        else:
            file_attribs, file_tags = xml_parse(root, file, args)
            for attrib in file_attribs:
                all_attribs[attrib] = all_attribs.get(attrib, 0) + 1
            for tag in file_tags:
                all_tags[tag] = all_tags.get(tag, 0) + 1

    if args.mapping_csv:
        return combined_dict
    elif args.attribute_tag_csv:
        return all_paths
    else:
        return uniq_data_to_dict(all_attribs, all_tags)

def xml_parse(root, filename, args, mapping_df=None):
    """Parse XML and collect data based on the selected mode."""
    all_tags, all_attribs, path_list, mapped_data = [], [], [], {}
    path_name = []

    def generate_attribute_permutations(attributes):
        keys = list(attributes.keys())
        return [
            {k: attributes[k] for k in combo}
            for r in range(1, len(keys) + 1)
            for combo in combinations(keys, r)
        ]

    for event, elem in root:
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

        if event == 'start':
            path_name.append(tag)
            current_path = '/'.join(path_name)
            attributes = elem.attrib

            if args.attribute_tag_csv:
                path_list.append(current_path)
            elif args.mapping_csv:
                mapped_data[current_path] = mapped_data.get(current_path, "")
                if elem.text:
                    mapped_data[current_path] += f" -- {elem.text.strip()}" if mapped_data[current_path] else elem.text.strip()
            else:
                all_tags.append(tag)

            if attributes:
                combined_attrs = ", ".join(f"@{k.split('}')[-1]}='{v}'" for k, v in attributes.items())
                combined_path = f"{current_path} [{combined_attrs}]"
                if args.attribute_tag_csv:
                    path_list.append(combined_path)
                elif args.mapping_csv:
                    mapped_data[combined_path] = mapped_data.get(combined_path, "")
                    if elem.text:
                        mapped_data[combined_path] += f" -- {elem.text.strip()}" if mapped_data[combined_path] else elem.text.strip()
                else:
                    all_attribs.extend(attributes.items())
                if len(attributes) > 1:
                    for perm in generate_attribute_permutations(attributes):
                        perm_attrs = ", ".join(f"@{k.split('}')[-1]}='{v}'" for k, v in perm.items())
                        perm_path = f"{current_path} [@{perm_attrs}]"
                        if args.attribute_tag_csv:
                            path_list.append(perm_path)
                        if arg.mapping_csv:
                            mapped_data[perm_path] = perm_attrs
            path_name[-1] = f"{tag} [{combined_attrs}]"

        elif event == 'end':
            path_name.pop()
            elem.clear()

    if args.attribute_tag_csv:
        return path_list
    elif args.mapping_csv:
        return compare_and_map(filename, mapped_data, mapping_df)
    else:
        return all_attribs, all_tags

def compare_and_map(filename, xml_data, mapping_df):
    """Map XML data to fields based on the mapping CSV."""
    print("=============== Compare and Map ===============")
    mapped_data = {"pid": get_pid(filename)}
    for path, field_name in zip(mapping_df["xpaths"], mapping_df["fields"]):
        value = xml_data.get(path, "").strip()
        if value:
            mapped_data[field_name] = f"{mapped_data.get(field_name, '')} -- {value}" if field_name in mapped_data else value
        else:
            mapped_data.setdefault(field_name, "")
    return mapped_data

def uniq_data_to_dict(all_attribs, all_tags):
    data = {
        'attributes': list(all_attribs.keys()),
        'attributes_count': list(all_attribs.values()),
        'tags': list(all_tags.keys()),
        'tags_count': list(all_tags.values())
    }
    max_length = max(len(data['attributes']), len(data['tags']))
    for key in data:
        data[key] += [np.nan] * (max_length - len(data[key]))
    return data


def write_to_csv(data, output_file, args):
    """Write the processed data to a CSV file."""
    if args.attribute_tag_csv:
        df = pd.DataFrame({"xpaths": list(data.keys()), "counts": list(data.values())})
        df.to_csv(output_file, index=False)
        print(f"Step 2 - All XPaths written to {output_file}")
    elif args.mapping_csv:
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f"Step 3 - Mapped data written to {output_file}")
    else:
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f"Step 1 - Attributes and tags data written to {output_file}")

# ----------------------------------------------------------------------
# Main Function
# ----------------------------------------------------------------------
def main():
    args = process_command_line_arguments()
    if args.input_directory and args.output_attribsTags:
        attrib_tags = initiate_parse(args.input_directory, args)
        write_to_csv(attrib_tags, args.output_attribsTags, args)
    elif args.input_directory and args.output_directory and args.attribute_tag_csv:
        all_paths = initiate_parse(args.input_directory, args)
        write_to_csv(all_paths, args.output_directory, args)
    elif args.mapping_csv and args.input_directory and args.output_directory:
        mapping_df = get_csv(args.mapping_csv, args)
        combined_data = initiate_parse(args.input_directory, args, mapping_df)
        write_to_csv(combined_data, args.output_directory, args)

if __name__ == "__main__":
    main()
