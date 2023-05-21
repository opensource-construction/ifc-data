import pandas as pd
import json
import argparse

# Define command line arguments
parser = argparse.ArgumentParser(description='Apply transformations to a CSV file based on conditions in a JSON file')
parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
parser.add_argument('json_file', type=str, help='Path to the JSON file with conditions and actions')
parser.add_argument('output_file', type=str, help='Path to the output CSV file')

args = parser.parse_args()

# Read in the CSV file and the JSON file
df = pd.read_csv(args.csv_file)
with open(args.json_file, 'r') as f:
    config = json.load(f)

# Total row count
total_row_count = len(df)

match_count = 0

# Apply each condition/action pair from the JSON file
for index, row in df.iterrows():
    for condition_group in config['condition_groups']:
        matched_all_conditions = True
        for condition in condition_group['conditions']:
            column = condition['column']
            values = condition['value'] if isinstance(condition['value'], list) else [condition['value']]
            operator = condition.get('operator', 'equals')  # Defaults to 'equals' if no operator provided

            if operator == 'equals':
                if row[column] not in values:
                    matched_all_conditions = False
                    break
            elif operator == 'contains':
                if not any(value in str(row[column]) for value in values):
                    matched_all_conditions = False
                    break

        if matched_all_conditions:
            match_count += 1
            if 'actions' in condition_group:  # Check if 'actions' key exists
                for action in condition_group['actions']:
                    if action['type'] == 'set':
                        df.at[index, action['target_column']] = action['value']
                    elif action['type'] == 'copy':
                        df.at[index, action['target_column']] = row[action['source_column']]

# Save the updated DataFrame to a new CSV file
df.to_csv(args.output_file, index=False)

print(f'Total number of rows: {total_row_count}')
print(f'Number of matches: {match_count}')
