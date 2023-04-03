import sys
import json
import ifcopenshell

def read_json_file(json_file_path):
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    return data

def read_ifc_file(ifc_file_path):
    ifc_file = ifcopenshell.open(ifc_file_path)
    return ifc_file

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


def write_json_file(json_file_path, data):
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)

def main(ifc_file_path, elements_filter_path, output_file_path):
    elements_filter = read_json_file(elements_filter_path)
    ifc_file = read_ifc_file(ifc_file_path)
    properties_filter = extract_properties(ifc_file, elements_filter)
    write_json_file(output_file_path, properties_filter)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_properties_filter.py <input.ifc> <elements_filter.json> <properties_filter.json>")
        sys.exit(1)

    ifc_file_path = sys.argv[1]
    elements_filter_path = sys.argv[2]
    output_file_path = sys.argv[3]
    main(ifc_file_path, elements_filter_path, output_file_path)
