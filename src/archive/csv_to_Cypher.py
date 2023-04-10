import csv
import os
import argparse

def generate_cypher_query(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)

        query = "LOAD CSV WITH HEADERS FROM 'file:///{}' AS row\n".format(os.path.basename(csv_file))
        query += "MERGE (e:Element {guid: row.GUID})\n"

        for header in headers:
            if header == "GUID":
                continue
            sanitized_header = header.replace(" ", "_").replace(".", "_")
            query += "SET e.{} = row.{}\n".format(sanitized_header, sanitized_header)

        return query

def main():
    parser = argparse.ArgumentParser(description="Generate Cypher query from CSV")
    parser.add_argument("input_csv", type=str, help="Path to input CSV file")
    parser.add_argument("output_file", type=str, help="Path to output file for Cypher query")

    args = parser.parse_args()

    cypher_query = generate_cypher_query(args.input_csv)

    with open(args.output_file, 'w') as f:
        f.write(cypher_query)

    print(f"Generated Cypher query saved to {args.output_file}")

if __name__ == "__main__":
    main()
