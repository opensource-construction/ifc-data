import argparse
import csv
import json

# Define command line arguments
parser = argparse.ArgumentParser(description='Update column names in a CSV file using a mapping file')
subparsers = parser.add_subparsers(title='commands', dest='command')

# Map command
map_parser = subparsers.add_parser('map', help='Update column names in a CSV file using a mapping file')
map_parser.add_argument('mapping_file', type=str, help='Path to the mapping CSV file')
map_parser.add_argument('input_file', type=str, help='Path to the input CSV file')
map_parser.add_argument('output_file', type=str, help='Path to the output CSV file')

# Copy command
copy_parser = subparsers.add_parser('copy', help='Copy values from one column to another')
copy_parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
copy_parser.add_argument('source_column', type=str, help='Name of the source column')
copy_parser.add_argument('target_column', type=str, help='Name of the target column')

# Match command
match_parser = subparsers.add_parser('match', help='Apply a transformation based on conditions specified in a JSON file')
match_parser.add_argument('json_file', type=str, help='Path to the JSON file with conditions and actions')
match_parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
match_parser.add_argument('output_file', type=str, help='Path to the output CSV file')

# Clean command
clean_parser = subparsers.add_parser('clean', help='Remove columns not specified in a JSON file')
clean_parser.add_argument('json_file', type=str, help='Path to the JSON file containing the list of columns to keep')
clean_parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
clean_parser.add_argument('output_file', type=str, help='Path to the output CSV file')


# Parse command line arguments
args = parser.parse_args()

if args.command == 'map':
    # Read in the mapping file
    mapping = {}
    with open(args.mapping_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            mapping[row[0]] = row[1]

    # Read in the input file and create a new file with updated headers
    with open(args.input_file, 'r') as f_in, open(args.output_file, 'w', newline='') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)

        # Update the header row with the new names from the mapping file
        header = next(reader)
        updated_header = []
        for col in header:
            if col in mapping:
                updated_header.append(mapping[col])
            else:
                updated_header.append(col)
        writer.writerow(updated_header)

        # Write the rest of the rows to the new file
        for row in reader:
            writer.writerow(row)

    print(f'Updated CSV written to {args.output_file}')

elif args.command == 'copy':
    # Read in the input CSV file
    with open(args.csv_file, 'r', newline='') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames
        data = [row for row in reader]

    source_column = args.source_column
    target_column = args.target_column

    # Check if the source column exists in the fieldnames
    if source_column not in fieldnames:
        raise ValueError(f"Source column '{source_column}' not found in the CSV file.")

    # Add the target column to the fieldnames if it doesn't exist
    if target_column not in fieldnames:
        fieldnames.append(target_column)

    # Perform the copy operation
    for row in data:
        row[target_column] = row[source_column]

    # Create the output file name by adding '_clean' before the extension
    output_file = args.csv_file.rsplit('.', 1)
    output_file = f'{output_file[0]}_clean.{output_file[1]}'

    # Write the updated data to the new file
    with open(output_file, 'w', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f'Updated CSV written to {output_file}')

# Match command
elif args.command == 'match':
    # Read in the JSON file
    with open(args.json_file, 'r') as f:
        config = json.load(f)

    # Read in the input CSV file
    with open(args.csv_file, 'r', newline='') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames
        data = [row for row in reader]

    # Process the conditions and actions specified in the JSON file
    updated_data = []
    for row in data:
        updated_row = row.copy()
        for condition in config['conditions']:
            column = condition['column']
            value = condition['value']

            if row[column] == value:
                action = condition['action']

                if action['type'] == 'copy':
                    source_column = action['source_column']
                    target_column = action['target_column']

                    # Check if the source column exists in the fieldnames
                    if source_column not in fieldnames:
                        raise ValueError(f"Source column '{source_column}' not found in the CSV file.")

                    # Add the target column to the fieldnames if it doesn't exist
                    if target_column not in fieldnames:
                        fieldnames.append(target_column)

                    updated_row[target_column] = row[source_column]
                    print(f"Copied value '{row[source_column]}' from '{source_column}' to '{target_column}'")
        updated_data.append(updated_row)

    # Write the updated data to the new file
    with open(args.output_file, 'w', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_data)

    print(f'Updated CSV written to {args.output_file}')

# Clean command
elif args.command == 'clean':
    # Read in the JSON file
    with open(args.json_file, 'r') as f:
        config = json.load(f)

    # Read in the input CSV file
    with open(args.csv_file, 'r', newline='') as f_in:
        reader = csv.DictReader(f_in)
        data = [row for row in reader]

    # Get the list of columns to keep from the JSON file
    columns_to_keep = config['columns']

    # Filter the data to only include the specified columns
    filtered_data = [{k: row[k] for k in columns_to_keep if k in row} for row in data]

    # Write the filtered data to the output file
    with open(args.output_file, 'w', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=columns_to_keep)
        writer.writeheader()
        writer.writerows(filtered_data)

    print(f'Cleaned CSV written to {args.output_file}')


else:
    parser.print_help()
