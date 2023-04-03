import argparse
import csv

# Define command line arguments
parser = argparse.ArgumentParser(description='Update column names in a CSV file using a mapping file')
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
        mapping[row[0]] = row[1]

# Read in the input file and create a new file with updated headers
with open(args.input, 'r') as f_in, open(args.output, 'w', newline='') as f_out:
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

print(f'Updated CSV written to {args.output}')