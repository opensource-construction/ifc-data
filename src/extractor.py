import sys
import os
import ifcopenshell
import ifcopenshell.util.element as Element
import ifcopenshell.util.placement as Placement
import pprint
import pandas as pd
import json
import numpy as np
import argparse
from tqdm import tqdm

pp = pprint.PrettyPrinter()

def get_object_coordinates(ifc_object):
    matrix = Placement.get_local_placement(ifc_object.ObjectPlacement)
    return matrix[:, 3][:3]

def get_element_orientation(ifc_object):
    matrix = Placement.get_local_placement(ifc_object.ObjectPlacement)
    return matrix[:3, :3]

def get_objects_data_by_class(file, class_type):
    def add_pset_attributes(psets):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(f'{pset_name}.{property_name}')

    pset_attributes = set()
    objects_data = []
    prop_data = []
    objects = file.by_type(class_type)  

    for object in objects:
        psets = Element.get_psets(object, psets_only=True)
        add_pset_attributes(psets)
        qtos = Element.get_psets(object, qtos_only=True)
        add_pset_attributes(qtos)

        object_id = object.id()
        coordinates = get_object_coordinates(object)
        orientation = get_element_orientation(object)  # Extract orientation
        objects_data.append({
            "ExpressID": object_id,
            "GlobalID": object.GlobalId,
            "Class": object.is_a(),
            "PredefinedType": Element.get_predefined_type(object),
            "Name": object.Name,
            "Level": Element.get_container(object).Name
            if Element.get_container(object)
            else "",
            "ObjectType": Element.get_type(object).Name
            if Element.get_type(object)
            else "",
            "QuantitySets": qtos,
            "PropertySets": psets,
            "Coord1": coordinates[0],
            "Coord2": coordinates[1],
            "Vector1": coordinates[2],
            "Orientation": orientation  # Include orientation in the object data
        })

        # get data for structure export
        for pset_type, pset_dict in [("PropertySet", psets), ("QuantitySet", qtos)]:
                    for pset_name, pset_data in pset_dict.items():
                        for prop_name in pset_data.keys():
                            prop_data.append((object.GlobalId, pset_type, pset_name, prop_name))


    return objects_data, prop_data, list(pset_attributes)

def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".", 1)[0]
        prop_name = attribute.split(".", -1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        if pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
    else:
        return None

import json

def convert_numpy_to_list(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value

def flatten_properties(object_data):
    flat_properties = {}
    for key, value in object_data.items():
        if key in ["PropertySets", "QuantitySets"]:
            for pset_name, pset_data in value.items():
                for prop_name, prop_value in pset_data.items():
                    flat_properties[f"{pset_name}.{prop_name}"] = convert_numpy_to_list(prop_value)
        elif key != "Name":
            flat_properties[key] = convert_numpy_to_list(value)
    return flat_properties

def write_json_files(data, output_path):
    elements_dir = os.path.join(output_path, "elements")
    os.makedirs(elements_dir, exist_ok=True)
    file_list = []

    for object_data in data:
        global_id = object_data["GlobalID"]
        json_file_name = f"{global_id}.json"
        file_list.append(json_file_name)

        properties = object_data.copy()
        del properties["Orientation"]

        element_data = {
            "Name": object_data["Name"],
        }
        element_data.update(flatten_properties(properties))

        with open(os.path.join(elements_dir, json_file_name), "w") as outfile:
            json.dump(element_data, outfile, ensure_ascii=False, indent=4)

    with open(os.path.join(output_path, "file_list.json"), "w") as outfile:
        json.dump(file_list, outfile, ensure_ascii=False, indent=4)

def main(input_file, output_folder, output_format):
    # Add progress bar (total=4 stages)
    with tqdm(total=4, desc="Progress", bar_format="{desc}: {percentage:.1f}%") as pbar:

        file = ifcopenshell.open(input_file)
        file_name = os.path.splitext(os.path.basename(input_file))[0]

        output_path = os.path.join(output_folder, file_name)
        os.makedirs(output_path, exist_ok=True)

        data, prop_data, pset_attributes = get_objects_data_by_class(file, "IfcBuildingElement")
        pbar.update(1)  # Update progress bar

        attributes = ["ExpressID", "GlobalID", "Class", "PredefinedType", "Name", "Level", "ObjectType", "Coord1", "Coord2", "Vector1", "Orientation"] + pset_attributes

        pandas_data = []
        for object_data in data:
            row = []
            for attribute in attributes:
                value = get_attribute_value(object_data, attribute)
                row.append(value)
            pandas_data.append(tuple(row))

        dataframe = pd.DataFrame.from_records(pandas_data, columns=attributes)
        pbar.update(1)  # Update progress bar

        # Export Property Sets and Quantity Sets to CSV
        prop_data_columns = ["BuildingElement", "TypeofPropertySet", "Property Set", "Property"]
        prop_data_dataframe = pd.DataFrame(prop_data, columns=prop_data_columns)

        # Remove duplicate rows from the DataFrame
        prop_data_dataframe = prop_data_dataframe.drop(columns=["BuildingElement"])
        prop_data_dataframe = prop_data_dataframe.drop_duplicates()
        
        prop_data_csv_file = os.path.join(output_path, f"{file_name}_property_data.csv")
        prop_data_dataframe.to_csv(prop_data_csv_file, index=False)
        print(" Property data CSV executed successfully")
        pbar.update(1)  # Update progress bar

        # Export to CSV
        if output_format == 'csv':
            csv_file = os.path.join(output_path, f"{file_name}.csv")
            dataframe.to_csv(csv_file)
            print(" CSV executed successfully")
            pbar.update(2) # Update progress bar

        # Export to Excel
        elif output_format == 'xls':
            excel_file = os.path.join(output_path, f"{file_name}.xlsx")
            writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
            for object_class in dataframe["Class"].unique():
                df_class = dataframe[dataframe["Class"] == object_class]
                df_class = df_class.dropna(axis=1, how='all')
                df_class.to_excel(writer, sheet_name=object_class, index=False)
            writer.save()
            print(" Excel executed successfully")
            pbar.update(2) # Update progress bar

        # Export to JSON
        elif output_format == 'json':
            write_json_files(data, output_path)
            print(" JSON executed successfully")
            pbar.update(2) # Update progress bar


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract element data from an IFC file")
    parser.add_argument("input_file", help="Path to the input IFC file")
    parser.add_argument("output_folder", help="Path to the output folder")
    parser.add_argument(
        "--out",
        choices=["csv", "xls", "json"],
        default="csv",
        help="Output format (csv, xls, or json)",
    )

    args = parser.parse_args()

    main(args.input_file, args.output_folder, args.out)
