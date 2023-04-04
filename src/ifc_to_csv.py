import argparse
import csv
import ifcopenshell
import json

def extract_element_properties(ifc_file, properties_to_include):
    property_data = {}
    property_names = []
    for properties in properties_to_include.values():
        property_names.extend(properties)

    for element in ifc_file.by_type("IfcElement"):
        guid = element.GlobalId
        properties_dict = {name: "" for name in property_names}

        if element.IsDefinedBy:
            for rel_defines in element.IsDefinedBy:
                if rel_defines.is_a("IfcRelDefinesByProperties"):
                    property_set = rel_defines.RelatingPropertyDefinition
                    if property_set.is_a("IfcPropertySet"):
                        for property in property_set.HasProperties:
                            property_name = property.Name
                            if property_name in property_names:
                                properties_dict[property_name] = property.NominalValue.wrappedValue
        property_data[guid] = properties_dict

    return property_data




def write_properties_to_csv(property_data, output_csv, properties_to_include):
    property_names = []
    for properties in properties_to_include.values():
        property_names.extend(properties)

    fieldnames = ['GlobalId'] + property_names

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for element_guid, properties in property_data.items():
            row = {'GlobalId': element_guid}
            row.update(properties)
            writer.writerow(row)



def main():
    parser = argparse.ArgumentParser(description="Extract IFC element properties and quantities to CSV.")
    parser.add_argument("ifc_file", help="Path to the input IFC file.")
    parser.add_argument("properties_json", help="Path to the JSON file containing properties to include.")
    parser.add_argument("--output-csv", help="Path to the output CSV file.", default="output.csv")

    args = parser.parse_args()

    with open(args.properties_json) as json_file:
        properties_to_include = json.load(json_file)

    ifc_file = ifcopenshell.open(args.ifc_file)
    property_data = extract_element_properties(ifc_file, properties_to_include)
    write_properties_to_csv(property_data, args.output_csv, properties_to_include)

if __name__ == "__main__":
    main()
