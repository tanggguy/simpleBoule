import salome
import math

salome.salome_init()
from salome.geom import geomBuilder

geompy = geomBuilder.New()

# 1. Parameters
L_cube = 0.01
R_sphere = 0.004
Center = L_cube / 2.0

# 2. Create Sphere (Solid Region)
# Center at (0.005, 0.005, 0.005)
Solid_Sphere = geompy.MakeSphereR(R_sphere)
geompy.TranslateDXDYDZ(Solid_Sphere, Center, Center, Center)
geompy.addToStudy(Solid_Sphere, "Solid_Sphere")

# 3. Create Box (Fluid Domain Boundaries)
# From (0,0,0) to (0.01, 0.01, 0.01)
Fluid_Domain = geompy.MakeBoxDXDYDZ(L_cube, L_cube, L_cube)
geompy.addToStudy(Fluid_Domain, "Fluid_Domain")

# 4. Create Groups on Box (Patches)
# Inlet: Face X = 0
inlet_faces = geompy.GetShapesOnPlaneWithNormal(Fluid_Domain, geompy.ShapeType["FACE"], 
                                                geompy.MakeVectorDXDYDZ(1, 0, 0), 
                                                geompy.MakeVertex(0, 0, 0))
inlet = geompy.CreateGroup(Fluid_Domain, geompy.ShapeType["FACE"])
geompy.UnionList(inlet, inlet_faces)
geompy.addToStudyInFather(Fluid_Domain, inlet, "inlet")

# Outlet: Face X = L_cube
outlet_faces = geompy.GetShapesOnPlaneWithNormal(Fluid_Domain, geompy.ShapeType["FACE"], 
                                                 geompy.MakeVectorDXDYDZ(1, 0, 0), 
                                                 geompy.MakeVertex(L_cube, 0, 0))
outlet = geompy.CreateGroup(Fluid_Domain, geompy.ShapeType["FACE"])
geompy.UnionList(outlet, outlet_faces)
geompy.addToStudyInFather(Fluid_Domain, outlet, "outlet")

# Walls: All other faces (Y=0, Y=L, Z=0, Z=L)
# We can get all faces and remove inlet/outlet, or select them explicitly.
# Explicit selection is safer.
wall_faces = []
# Y=0
wall_faces.extend(geompy.GetShapesOnPlaneWithNormal(Fluid_Domain, geompy.ShapeType["FACE"], 
                                                    geompy.MakeVectorDXDYDZ(0, 1, 0), 
                                                    geompy.MakeVertex(0, 0, 0)))
# Y=L
wall_faces.extend(geompy.GetShapesOnPlaneWithNormal(Fluid_Domain, geompy.ShapeType["FACE"], 
                                                    geompy.MakeVectorDXDYDZ(0, 1, 0), 
                                                    geompy.MakeVertex(0, L_cube, 0)))
# Z=0
wall_faces.extend(geompy.GetShapesOnPlaneWithNormal(Fluid_Domain, geompy.ShapeType["FACE"], 
                                                    geompy.MakeVectorDXDYDZ(0, 0, 1), 
                                                    geompy.MakeVertex(0, 0, 0)))
# Z=L
wall_faces.extend(geompy.GetShapesOnPlaneWithNormal(Fluid_Domain, geompy.ShapeType["FACE"], 
                                                    geompy.MakeVectorDXDYDZ(0, 0, 1), 
                                                    geompy.MakeVertex(0, 0, L_cube)))

walls = geompy.CreateGroup(Fluid_Domain, geompy.ShapeType["FACE"])
geompy.UnionList(walls, wall_faces)
geompy.addToStudyInFather(Fluid_Domain, walls, "walls")


# 5. Export STL
# Ensure directory exists (handled by user/system usually, but good to note)
# Export Solid Sphere
geompy.ExportSTL(Solid_Sphere, "../constant/triSurface/sphere.stl", True, 1e-5, True)

# Export Fluid Domain with Patches
# We export the groups as separate STLs or the whole domain? 
# snappyHexMesh usually likes separate STLs for patches if we want to name them, 
# OR a single STL with named regions (ASCII STL with "solid name").
# Salome ExportSTL exports the shape. If we want named patches in one file, it's tricky with basic ExportSTL.
# Standard OpenFOAM workflow with Salome often involves exporting each group to a separate STL file, 
# or using a script to combine them.
# However, the requirements say:
# "Fichier 2 : La Boîte ... contenant les groupes inlet, outlet, walls"
# "Chemin : ../constant/triSurface/box_walls.stl"
# If we export the box, it's just a box. 
# Let's export the groups individually and also the full box if needed, 
# BUT the prompt implies a single file for the box patches?
# Actually, snappyHexMesh can read a multi-solid STL. 
# Let's export individual patch files for clarity and robustness with snappy, 
# OR try to merge them. 
# Given the requirement "box_walls.stl", let's try to export the groups into one file if possible,
# or just export the groups separately and let the user/snappy handle it.
# BUT, looking at the previous script `__MAIN__Geom_salome.py`, it used `sed` to rename the solid in the STL.
# Let's follow that pattern or a cleaner one.
# The requirement says "Fichier 2 ... box_walls.stl".
# If I export `Fluid_Domain`, it won't have the patch names in the STL solid names by default.
# I will export the groups separately to be safe and standard, 
# AND I will also create a combined `box_walls.stl` if that's strictly what's asked, 
# but usually `snappyHexMesh` prefers `inlet.stl`, `outlet.stl`, `walls.stl` if we want to define patches easily.
# Wait, `snappyHexMeshDict` can take one STL with multiple regions.
# Let's export the groups to separate files first, as it is easier to manage.
# Re-reading requirement: "Fichier 2 : La Boîte ... Chemin : ../constant/triSurface/box_walls.stl"
# Maybe it implies a single file. 
# I will export `inlet`, `outlet`, `walls` to `box_walls.stl` by appending? Salome doesn't do append easily.
# I will export them as `box_inlet.stl`, `box_outlet.stl`, `box_walls.stl` (for the walls part).
# Actually, let's stick to the plan:
# "geometry { ... box_walls.stl { type triSurfaceMesh; name box_walls; regions { inlet { name inlet; } ... } } }"
# This implies `box_walls.stl` contains solids named `inlet`, `outlet`, `walls`.
# I can achieve this by exporting separate files and concatenating them, or using a helper.
# Since I cannot easily run `cat` inside the python script without OS calls (which is fine),
# I will export separate files: `box_inlet.stl`, `box_outlet.stl`, `box_walls_faces.stl`.
# Then I will use python to concatenate them into `box_walls.stl` with proper solid names.

import os

tri_surface_dir = "../constant/triSurface"
if not os.path.exists(tri_surface_dir):
    os.makedirs(tri_surface_dir)

# Export individual patches
file_inlet = os.path.join(tri_surface_dir, "box_inlet.stl")
geompy.ExportSTL(inlet, file_inlet, True, 1e-5, True)

file_outlet = os.path.join(tri_surface_dir, "box_outlet.stl")
geompy.ExportSTL(outlet, file_outlet, True, 1e-5, True)

file_walls = os.path.join(tri_surface_dir, "box_walls_faces.stl")
geompy.ExportSTL(walls, file_walls, True, 1e-5, True)

# Function to change solid name in STL and read content
def read_and_rename(filename, new_name):
    with open(filename, 'r') as f:
        content = f.read()
    # Replace "solid ..." with "solid new_name"
    # The first line is "solid <something>"
    # The last line is "endsolid <something>"
    lines = content.splitlines()
    if lines:
        lines[0] = f"solid {new_name}"
        lines[-1] = f"endsolid {new_name}"
    return "\n".join(lines) + "\n"

# Concatenate into box_walls.stl
final_box_file = os.path.join(tri_surface_dir, "box_walls.stl")
with open(final_box_file, 'w') as outfile:
    outfile.write(read_and_rename(file_inlet, "inlet"))
    outfile.write(read_and_rename(file_outlet, "outlet"))
    outfile.write(read_and_rename(file_walls, "walls"))

# Clean up temporary files
os.remove(file_inlet)
os.remove(file_outlet)
os.remove(file_walls)

print("Geometry generation complete.")
print(f"Exported: {os.path.abspath('../constant/triSurface/sphere.stl')}")
print(f"Exported: {os.path.abspath(final_box_file)}")
