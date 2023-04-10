import argparse
import csv
import json
from collections import defaultdict

def read_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]

def element_types(data):
    element_info = defaultdict(lambda: {'count': 0, 'element_names': set(), 'gross_area': 0})

    for row in data:
        element_type = row['vyzn.reference.ElementType']
        element_name = row['vyzn.source.ElementName']
        gross_area = row['vyzn.GrossArea']

        element_info[element_type]['count'] += 1
        element_info[element_type]['element_names'].add(element_name)
        
        if gross_area:
            element_info[element_type]['gross_area'] += float(gross_area)

    result = [{"ElementType": key,
               "Count": value['count'],
               "ElementNamesSummary": " ".join(value['element_names']),
               "GrossArea": value['gross_area']} for key, value in element_info.items()]
    return result


def main():
    parser = argparse.ArgumentParser(description="Read data from a CSV file and write multiple output files.")
    parser.add_argument("csv_file", help="Path to the CSV file")
    parser.add_argument("output_type", choices=["ElementTypes"], help="Type of output file to generate")
    parser.add_argument("output_file", help="Path to the output JSON file")
    args = parser.parse_args()

    data = read_csv(args.csv_file)

    if args.output_type == "ElementTypes":
        result = element_types(data)

    with open(args.output_file, "w") as file:
        json.dump(result, file, indent=2)

    print(f"Output saved to {args.output_file}")

if __name__ == "__main__":
    main()
