import sys
import csv
import json
import argparse
import ifcopenshell

def read_json_file(json_file_path):
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    return data

def read_ifc_file(ifc_file_path):
    ifc_file = ifcopenshell.open(ifc_file_path)
    return ifc_file

def extract_building_elements(ifc_file):
    building_elements = ifc_file.by_type("IfcBuildingElement")
    return building_elements

def extract_building_element_types(ifc_file):
    building_elements = ifc_file.by_type("IfcBuildingElement")
    building_element_types = set()

    for element in building_elements:
        if element.is_a("IfcBuildingElement"):
            building_element_types.add(element.is_a())

    return list(building_element_types)



def extract_properties(ifc_file, elements_filter):
    properties_filter = {}
    for item in ifc_file:
        if item.is_a() in elements_filter:
            for rel in item.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    prop_def = rel.RelatingPropertyDefinition
                    if prop_def.is_a("IfcPropertySet"):
                        prop_set_name = prop_def.Name
                        if prop_set_name not in properties_filter:
                            properties_filter[prop_set_name] = []
                        for prop in prop_def.HasProperties:
                            if prop.Name not in properties_filter[prop_set_name]:
                                properties_filter[prop_set_name].append(prop.Name)
    return properties_filter

def write_csv_file(csv_file_path, data, headers):
    with open(csv_file_path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for row_data in data:
            writer.writerow(row_data)

def write_json_file(json_file_path, data):
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)

def main(args):
    ifc_file = read_ifc_file(args.input_ifc)

    if args.extract_elements:
        building_elements = extract_building_elements(ifc_file)
        write_csv_file(args.output_file, [(elem.GlobalId,) for elem in building_elements], ['ID'])
        print(f"{len(building_elements)} elements extracted.")
    elif args.extract_element_types:
        building_element_types = extract_building_element_types(ifc_file)
        write_csv_file(args.output_file, [(elem,) for elem in building_element_types], ['Type'])
        print(f"{len(building_element_types)} building element types extracted.")
    elif args.extract_properties:
        if args.elements_filter:
            elements_filter = read_json_file(args.elements_filter)
        else:
            elements_filter = extract_building_element_types(ifc_file)

        properties_filter = extract_properties(ifc_file, elements_filter)
        write_json_file(args.output_file, properties_filter)
        properties_count = sum([len(props) for props in properties_filter.values()])
        print(f"{properties_count} properties extracted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract building elements, element types, or properties from an IFC file.")
    parser.add_argument("input_ifc", help="Path to the input IFC file.")
    parser.add_argument("output_file", help="Path to the output file (CSV for elements and element types, JSON for properties).")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--extract-elements", action="store_true", help="Extract building elements and write their IDs to a CSV file.")
    group.add_argument("--extract-element-types", action="store_true", help="Extract building element types and write their names to a CSV file.")
    group.add_argument("--extract-properties", action="store_true", help="Extract properties of building elements and write them to a JSON file.")
    
    parser.add_argument("--elements-filter", help="Path to the JSON file with elements filter (optional for --extract-properties).")

    args = parser.parse_args()

    main(args)

