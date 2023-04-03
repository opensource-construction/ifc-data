#!/usr/bin/env python3

import argparse
import ifcopenshell
import csv
import json
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="IFC Quality Check - A command line tool to extract information from IFC files"
    )
    parser.add_argument("ifc_file", help="Path to the IFC file")
    parser.add_argument("--version", action="store_true", help="Extract the IFC version from the input file")
    parser.add_argument("--IfcWall", action="store_true", help="Count all building elements with the value 'IfcWall'")
    parser.add_argument("--list-building-elements", action="store_true", help="List all different building elements and their counts")
    parser.add_argument("--output-csv", type=str, help="Path to the CSV file to store building element properties")
    parser.add_argument("--PSets", type=str, help="JSON file containing the list of property sets and quantity sets to include in the CSV export")

    args = parser.parse_args()

    if args.PSets:
        with open(args.PSets, "r") as json_file:
            args.property_and_quantity_sets_to_include = json.load(json_file)
    else:
        args.property_and_quantity_sets_to_include = None

    return args




def get_ifc_version(ifc_file):
    try:
        ifc_file = ifcopenshell.open(ifc_file)
        ifc_schema = ifc_file.wrapped_data.schema
        return ifc_schema
    except Exception as e:
        print(f"Error: {e}")
        return None


def count_walls(ifc_file):
    try:
        ifc_file = ifcopenshell.open(ifc_file)
        walls = ifc_file.by_type("IfcWall")
        return len(walls)
    except Exception as e:
        print(f"Error: {e}")
        return None


def list_building_elements(ifc_file):
    try:
        ifc_file = ifcopenshell.open(ifc_file)
        elements = ifc_file.by_type("IfcBuildingElement")
        element_counts = {}

        for element in elements:
            element_type = element.is_a()
            if element_type in element_counts:
                element_counts[element_type] += 1
            else:
                element_counts[element_type] = 1

        return element_counts
    except Exception as e:
        print(f"Error: {e}")
        return None


def extract_element_properties(ifc_file, property_and_quantity_sets_to_include):
    ifc_file = ifcopenshell.open(ifc_file)
    elements = ifc_file.by_type("IfcBuildingElement")

    property_data = []

    for element in elements:
        element_guid = element.GlobalId
        element_type = element.is_a()

        element_properties = {
            "ElementType": element_type,
            "GlobalId": element_guid
        }

        defined_props = element.IsDefinedBy
        for defined in defined_props:
            if defined.is_a("IfcRelDefinesByProperties"):
                relating_property_definition = defined.RelatingPropertyDefinition

                # Extract properties
                if relating_property_definition.is_a("IfcPropertySet"):
                    property_set_name = relating_property_definition.Name
                    if property_set_name in property_and_quantity_sets_to_include["Properties"]:
                        for prop in relating_property_definition.HasProperties:
                            property_name = prop.Name
                            if prop.is_a("IfcPropertySingleValue"):
                                property_value = prop.NominalValue.wrappedValue if prop.NominalValue is not None else None
                            else:
                                property_value = None

                            element_properties[f"{property_set_name}.{property_name}"] = property_value

                # Extract quantities
                if relating_property_definition.is_a("IfcElementQuantity"):
                    quantity_set_name = relating_property_definition.Name
                    if quantity_set_name in property_and_quantity_sets_to_include["Quantities"]:
                        for quantity in relating_property_definition.Quantities:
                            quantity_name = quantity.Name
                            if quantity.is_a("IfcQuantityLength"):
                                quantity_value = quantity.LengthValue if quantity.LengthValue is not None else None
                            elif quantity.is_a("IfcQuantityArea"):
                                quantity_value = quantity.AreaValue if quantity.AreaValue is not None else None
                            elif quantity.is_a("IfcQuantityVolume"):
                                quantity_value = quantity.VolumeValue if quantity.VolumeValue is not None else None
                            elif quantity.is_a("IfcQuantityCount"):
                                quantity_value = quantity.CountValue if quantity.CountValue is not None else None
                            elif quantity.is_a("IfcQuantityWeight"):
                                quantity_value = quantity.WeightValue if quantity.WeightValue is not None else None
                            elif quantity.is_a("IfcQuantityTime"):
                                quantity_value = quantity.TimeValue if quantity.TimeValue is not None else None
                            else:
                                quantity_value = None

                            element_properties[f"{quantity_set_name}.{quantity_name}"] = quantity_value

        property_data.append(element_properties)

    return property_data



def write_properties_to_csv(property_data, output_csv, property_and_quantity_sets_to_include=None):
    # Get all unique property set, property names, and quantity names
    property_names = {"GlobalId", "ElementType"}
    if property_and_quantity_sets_to_include is not None:
        for properties in property_and_quantity_sets_to_include.values():
            for property_name in properties:
                property_names.add(property_name)

    for properties in property_data:
        for property_name in properties.keys():

            property_names.add(property_name)

    # Write properties and quantities to CSV
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=property_names)
        writer.writeheader()
        for element_guid, properties in property_data.items():
            writer.writerow(properties)



def debug_element_properties_and_quantities(ifc_file):
    ifc_file = ifcopenshell.open(ifc_file)
    elements = ifc_file.by_type("IfcBuildingElement")

    for element in elements:
        element_guid = element.GlobalId
        element_type = element.is_a()

        print(f"Element {element_guid}:")
        print(f"  ElementType: {element_type}")

        defined_props = element.IsDefinedBy
        for defined in defined_props:
            if defined.is_a("IfcRelDefinesByProperties"):
                relating_property_definition = defined.RelatingPropertyDefinition

                # Print properties
                if relating_property_definition.is_a("IfcPropertySet"):
                    property_set_name = relating_property_definition.Name

                    print(f"  PropertySet: {property_set_name}")
                    for prop in relating_property_definition.HasProperties:
                        property_name = prop.Name
                        if prop.is_a("IfcPropertySingleValue"):
                            property_value = prop.NominalValue.wrappedValue if prop.NominalValue is not None else None
                        else:
                            property_value = None

                        print(f"    {property_name}: {property_value}")
                
                # Print quantities
                if relating_property_definition.is_a("IfcElementQuantity"):
                    quantity_set_name = relating_property_definition.Name

                    print(f"  QuantitySet: {quantity_set_name}")
                    for quantity in relating_property_definition.Quantities:
                        quantity_name = quantity.Name
                        if quantity.is_a("IfcQuantityLength"):
                            quantity_value = quantity.LengthValue if quantity.LengthValue is not None else None
                        elif quantity.is_a("IfcQuantityArea"):
                            quantity_value = quantity.AreaValue if quantity.AreaValue is not None else None
                        elif quantity.is_a("IfcQuantityVolume"):
                            quantity_value = quantity.VolumeValue if quantity.VolumeValue is not None else None
                        elif quantity.is_a("IfcQuantityCount"):
                            quantity_value = quantity.CountValue if quantity.CountValue is not None else None
                        elif quantity.is_a("IfcQuantityWeight"):
                            quantity_value = quantity.WeightValue if quantity.WeightValue is not None else None
                        elif quantity.is_a("IfcQuantityTime"):
                            quantity_value = quantity.TimeValue if quantity.TimeValue is not None else None
                        else:
                            quantity_value = None

                        print(f"    {quantity_name}: {quantity_value}")



def main():
    args = parse_arguments()

    if args.output_csv:
        if args.PSets is not None:
            with open(args.PSets, "r") as filter_file:
                property_and_quantity_sets_to_include = json.load(filter_file)
        else:
            property_and_quantity_sets_to_include = {"Properties": [], "Quantities": []}

        property_data = extract_element_properties(args.ifc_file, property_and_quantity_sets_to_include)
        write_properties_to_csv(property_data, args.output_csv, args.property_and_quantity_sets_to_include)
        print(f"Building element properties and quantities saved to {args.output_csv}")

    if args.version:
        ifc_version = get_ifc_version(args.ifc_file)
        if ifc_version:
            print(f"IFC version: {ifc_version}")
        else:
            print("Failed to extract IFC version.")

    if args.count_walls:
        num_walls = count_walls(args.ifc_file)
        if num_walls is not None:
            print(f"Number of walls: {num_walls}")
        else:
            print("Failed to count walls.")

    if args.IfcWall:
        num_walls = count_walls(args.ifc_file)
        if num_walls is not None:
            print(f"Number of IfcWall elements: {num_walls}")
        else:
            print("Failed to count IfcWall elements.")

    if args.list_building_elements:
        building_element_counts = list_building_elements(args.ifc_file)
        if building_element_counts:
            print("Building elements and counts:")
            for element_type, count in building_element_counts.items():
                print(f"{element_type}: {count}")
        else:
            print("Failed to list building elements.")




def log_property_data(property_data):
    print("\nProperty data:")
    for idx, properties in enumerate(property_data):
        print(f"\nElement {idx + 1}:")
        for key, value in properties.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()

