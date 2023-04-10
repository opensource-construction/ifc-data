import csv
import svgwrite
import argparse

def read_csv(input_csv):
    walls = []
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            walls.append({
                "start": (float(row["Coord1"]), float(row["Coord2"])),
                "vector": (float(row["Vector1"]), float(row["Vector2"])),
                "length": float(row["WallLength"])
            })
    return walls

def draw_floor_plan(walls, output_svg):
    dwg = svgwrite.Drawing(output_svg, profile='tiny', size=('1000px', '1000px'))

    for wall in walls:
        start = wall["start"]
        vector = wall["vector"]
        length = wall["length"]
        end = (start[0] + vector[0] * length, start[1] + vector[1] * length)
        dwg.add(dwg.line(start, end, stroke='black', stroke_width=1))

    dwg.save()

def main(input_csv, output_svg):
    walls = read_csv(input_csv)
    draw_floor_plan(walls, output_svg)
    print(f'SVG floor plan saved to {output_svg}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an SVG floor plan from a CSV file with wall coordinates and vectors')
    parser.add_argument('input_csv', type=str, help='Path to the input CSV file')
    parser.add_argument('output_svg', type=str, help='Path to the output SVG file')
    args = parser.parse_args()

    main(args.input_csv, args.output_svg)
