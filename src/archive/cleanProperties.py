import argparse
import csv

# Define command line arguments
parser = argparse.ArgumentParser(description='Filter columns in a CSV file using a mapping file')
parser.add_argument('mapping', type=str, help='Path to the mapping CSV file')
parser.add_argument('input', type=str, help='Path to the input CSV file')
parser.add_argument('output', type=str, help='Path to the output CSV file')

# Parse command line arguments
args = parser.parse_args()

# Read in the mapping file
mapping = {}
with open(args.mapping, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        mapping[row[0]] = row[0]

# Read in the input file and create a new file with filtered columns
with open(args.input, 'r') as f_in, open(args.output, 'w', newline='') as f_out:
    reader = csv.DictReader(f_in)

    # Print the column names from the input CSV
    print("Input CSV column names:", reader.fieldnames)

    filtered_fieldnames = [col for col in reader.fieldnames if col in mapping]
    writer = csv.DictWriter(f_out, fieldnames=filtered_fieldnames)

    # Write the filtered header row
    writer.writeheader()

    # Write the rest of the rows to the new file, keeping only the specified columns
    row_count = 0
    for row in reader:
        filtered_row = {mapping[col]: row[col] for col in mapping if col in row}
        writer.writerow(filtered_row)
        row_count += 1

print(f'Filtered CSV written to {args.output}')
print(f'Columns created in the new CSV: {", ".join(filtered_fieldnames)}')
print(f'Number of rows written: {row_count}')
