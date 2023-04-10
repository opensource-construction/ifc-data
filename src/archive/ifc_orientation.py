import ifcopenshell
import math

def get_orientation_from_placement(placement):
    if not placement:
        return None

    if isinstance(placement, ifcopenshell.entity_instance):
        placement = placement.wrappedValue

    z_axis = placement.Axis
    ref_direction = placement.RefDirection

    if not z_axis or not ref_direction:
        return None

    x_axis = [
        ref_direction[1] * z_axis[2] - ref_direction[2] * z_axis[1],
        ref_direction[2] * z_axis[0] - ref_direction[0] * z_axis[2],
        ref_direction[0] * z_axis[1] - ref_direction[1] * z_axis[0],
    ]

    orientation_matrix = [
        [x_axis[0], ref_direction[0], z_axis[0]],
        [x_axis[1], ref_direction[1], z_axis[1]],
        [x_axis[2], ref_direction[2], z_axis[2]],
    ]

    return orientation_matrix

def radians_to_degrees(radians):
    return radians * 180 / math.pi

def get_element_orientation(element):
    if not element.ObjectPlacement:
        return None

    if isinstance(element.ObjectPlacement, ifcopenshell.entity_instance):
        placement = element.ObjectPlacement.RelativePlacement

    return get_orientation_from_placement(placement)

filename = 'path/to/your/ifc/file.ifc'
ifc_file = ifcopenshell.open(filename)

# Extract project orientation
project = ifc_file.by_type('IfcProject')[0]
sites = ifc_file.by_type('IfcSite')
buildings = ifc_file.by_type('IfcBuilding')

if sites:
    site = sites[0]
    project_orientation = get_orientation_from_placement(site.ObjectPlacement.RelativePlacement)
elif buildings:
    building = buildings[0]
    project_orientation = get_orientation_from_placement(building.ObjectPlacement.RelativePlacement)
else:
    project_orientation = None

print("Project Orientation:")
print(project_orientation)

# Extract orientations of elements
elements = ifc_file.by_type('IfcElement')
for element in elements:
    orientation = get_element_orientation(element)
    print(f"{element.GlobalId} Orientation:")
    print(orientation)
