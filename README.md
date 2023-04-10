# IFC-Data

This is an experimental collection of tools to work with IFC-data. 

It contains an IFC_TO_CSV script (src/ifc_extractor.py) that extracts all IFC properties (PropertySets and QuantitySets) for all BuildingElements and outputs it to CSV, XLS and JSON. It provides some basic data transformation and cleansing (src/ifc_transformer.py) and it also shows the results on a webpage (index.html?project-name=).

The ifc_extractor uses Ifcopenshell - many thanks to those lovely people.

# Data Extraction
## extractor

Put your ifc-file in the data folder and run this command. The script will create a folder with the IFC-file-name.

run: `python src/extractor.py <input_ifc_file> <output_folder>`

example: `python src/extractor.py data/Astra.ifc data`

## transformer

This Python script provides a command-line tool to perform various transformations on CSV files. It currently supports the following commands:

1. **map**: Update column names in the CSV file using a mapping file
2. **copy**: Copy values from one column to another in a CSV file
3. **match**: Perform conditional transformations based on a JSON configuration file

## Requirements

- Python 3.6 or higher

## Usage

### map

Update column names in a CSV file using a mapping file.

run: `python ifc_transform.py map <mapping_file> <input_file> <output_file>`

- `mapping_file`: Path to the mapping CSV file
- `input_file`: Path to the input CSV file
- `output_file`: Path to the output CSV file

The mapping file should be a CSV file with two columns. The first column contains the original column names, and the second column contains the new column names.

### copy

Copy values from one column to another in a CSV file.

python ifc_transform.py copy <csv_file> <source_column> <target_column>


- `csv_file`: Path to the input CSV file
- `source_column`: Name of the source column
- `target_column`: Name of the target column

The script creates a new CSV file with the same name as the input file, but with a "_clean" suffix.

### match

Perform conditional transformations based on a JSON configuration file.

python ifc_transform.py match <json_file> <csv_file> <output_file>


- `json_file`: Path to the JSON configuration file
- `csv_file`: Path to the input CSV file
- `output_file`: Path to the output CSV file

The JSON configuration file should contain an array of condition objects with the following structure:

```json
{
  "conditions": [
    {
      "column": "ColumnName",
      "value": "ValueToMatch",
      "action": {
        "type": "copy",
        "source_column": "SourceColumnName",
        "target_column": "TargetColumnName"
      }
    }
  ]
}`

Each condition object specifies a column and a value to match, as well as an action to perform when the condition is met. In this example, the action type is "copy", which means we want to copy the value from one column to another. The "source_column" and "target_column" properties within the "action" object define the source and target columns for the copy operation.

# Dashboard
## IFC Data Website

There is a basic dashboard that shows a summary of the data for ElementTypes and ElementNames and has dynamic search. 
This is still in development and does probably not work well with other IFC models.

# Chat
## IFC Building Chat 

There is a basic script to summarize content from the CSV that has been extracted. It creates a JSON with summary data for ElementTypes (ElementName content and GrossArea).

python src/summarizer.py <input_file.csv> <output_type> <output_file.json>

That file can be uploaded on the chat.html page and then you can ask ChatGPT a question about the building. 

Flask: requires that you run the Flask server and provide your OPENAI_API_KEY in your .ENV: python src/chat.py will start the Flask server on 127.0.0.1:5001

