import sys
import salome
import math
import os

salome.salome_init()
from salome.geom import geomBuilder

geompy = geomBuilder.New()

# ==========================================
# 1. Paramètres
# ==========================================
L_cube = 0.01
R_sphere = 0.004
Center = L_cube / 2.0
epaisseur_Box_Walls = 0.001

# ==========================================
# 2. Création de la Sphère (Solide)
# ==========================================
Solid_Sphere = geompy.MakeSphereR(R_sphere)
geompy.TranslateDXDYDZ(Solid_Sphere, Center, Center, Center)
geompy.addToStudy(Solid_Sphere, "Solid_Sphere")

# ==========================================
# 3. Création de la Boîte (Domaine Fluide)
# ==========================================
Fluid_Domain = geompy.MakeBoxDXDYDZ(L_cube, L_cube, L_cube)
geompy.addToStudy(Fluid_Domain, "Fluid_Domain")

# ==========================================
# 4. Création des Murs (Boîtes solides)
# ==========================================

# --- Mur X_min (Côté Inlet) ---
# Dimensions : épaisseur en X
box_walls_xmin = geompy.MakeBoxDXDYDZ(epaisseur_Box_Walls, L_cube, L_cube)
# On le recule pour qu'il touche X=0 (de -epaisseur à 0)
geompy.TranslateDXDYDZ(box_walls_xmin, -epaisseur_Box_Walls, 0, 0)
geompy.addToStudy(box_walls_xmin, "box_walls_xmin")

# --- Mur X_max (Côté Outlet) ---
# Dimensions : épaisseur en X
box_walls_xmax = geompy.MakeBoxDXDYDZ(epaisseur_Box_Walls, L_cube, L_cube)
# On l'avance pour qu'il commence à L (de L à L+epaisseur)
geompy.TranslateDXDYDZ(box_walls_xmax, L_cube, 0, 0)
geompy.addToStudy(box_walls_xmax, "box_walls_xmax")


# ==========================================
# 5. Création des Groupes (5 faces dans Walls)
# ==========================================
def get_face_at(shape, x, y, z):
    p = geompy.MakeVertex(x, y, z)
    return geompy.GetFaceNearPoint(shape, p)

# --- GROUPE INLET (1 face) ---
# Face tout à gauche (externe) : X = -epaisseur
face_inlet = get_face_at(box_walls_xmin, -epaisseur_Box_Walls, Center, Center)
inlet = geompy.CreateGroup(box_walls_xmin, geompy.ShapeType["FACE"])
geompy.UnionList(inlet, [face_inlet])
geompy.addToStudyInFather(box_walls_xmin, inlet, "inlet")

# --- GROUPE WALLS XMIN (5 faces) ---
faces_xmin_walls = [
    # Les 4 côtés (on vise le milieu de l'épaisseur du mur)
    get_face_at(box_walls_xmin, -epaisseur_Box_Walls/2, 0, Center),       # Y=0
    get_face_at(box_walls_xmin, -epaisseur_Box_Walls/2, L_cube, Center),  # Y=L
    get_face_at(box_walls_xmin, -epaisseur_Box_Walls/2, Center, 0),       # Z=0
    get_face_at(box_walls_xmin, -epaisseur_Box_Walls/2, Center, L_cube),  # Z=L
    # La 5ème face (Interne, contact fluide) : X = 0
    get_face_at(box_walls_xmin, 0, Center, Center)                        # X=0
]
walls_xmin = geompy.CreateGroup(box_walls_xmin, geompy.ShapeType["FACE"])
geompy.UnionList(walls_xmin, faces_xmin_walls)
geompy.addToStudyInFather(box_walls_xmin, walls_xmin, "walls_xmin")


# --- GROUPE OUTLET (1 face) ---
# Face tout à droite (externe) : X = L + epaisseur
face_outlet = get_face_at(box_walls_xmax, L_cube + epaisseur_Box_Walls, Center, Center)
outlet = geompy.CreateGroup(box_walls_xmax, geompy.ShapeType["FACE"])
geompy.UnionList(outlet, [face_outlet])
geompy.addToStudyInFather(box_walls_xmax, outlet, "outlet")

# --- GROUPE WALLS XMAX (5 faces) ---
faces_xmax_walls = [
    # Les 4 côtés
    get_face_at(box_walls_xmax, L_cube + epaisseur_Box_Walls/2, 0, Center),       # Y=0
    get_face_at(box_walls_xmax, L_cube + epaisseur_Box_Walls/2, L_cube, Center),  # Y=L
    get_face_at(box_walls_xmax, L_cube + epaisseur_Box_Walls/2, Center, 0),       # Z=0
    get_face_at(box_walls_xmax, L_cube + epaisseur_Box_Walls/2, Center, L_cube),  # Z=L
    # La 5ème face (Interne, contact fluide) : X = L
    get_face_at(box_walls_xmax, L_cube, Center, Center)                           # X=L
]
walls_xmax = geompy.CreateGroup(box_walls_xmax, geompy.ShapeType["FACE"])
geompy.UnionList(walls_xmax, faces_xmax_walls)
geompy.addToStudyInFather(box_walls_xmax, walls_xmax, "walls_xmax")


# ==========================================
# 6. Export STL
# ==========================================
tri_surface_dir = os.path.abspath("../constant/triSurface")
if not os.path.exists(tri_surface_dir):
    try:
        os.makedirs(tri_surface_dir)
    except OSError:
        pass 

print(f"Dossier d'export : {tri_surface_dir}")

# 1. Export de la Sphère
geompy.ExportSTL(Solid_Sphere, os.path.join(tri_surface_dir, "sphere.stl"), True, 1e-5, True)

# 2. Export combiné des patchs de la boîte
files_to_merge = []

def export_temp(shape, solid_name, temp_filename):
    fname = os.path.join(tri_surface_dir, temp_filename)
    geompy.ExportSTL(shape, fname, True, 1e-5, True)
    return (fname, solid_name)

# On ajoute tous les morceaux
files_to_merge.append(export_temp(inlet, "inlet", "tmp_inlet.stl"))
files_to_merge.append(export_temp(outlet, "outlet", "tmp_outlet.stl"))
# Ici, on regroupe les deux ensembles de murs sous le nom unique "walls"
files_to_merge.append(export_temp(walls_xmin, "walls", "tmp_walls_min.stl"))
files_to_merge.append(export_temp(walls_xmax, "walls", "tmp_walls_max.stl"))

def read_rename_delete(filepath, new_solid_name):
    with open(filepath, 'r') as f:
        content = f.read()
    lines = content.splitlines()
    if lines:
        lines[0] = f"solid {new_solid_name}"
        lines[-1] = f"endsolid {new_solid_name}"
    os.remove(filepath)
    return "\n".join(lines) + "\n"

final_box_file = os.path.join(tri_surface_dir, "box_walls.stl")
with open(final_box_file, 'w') as outfile:
    for fpath, sname in files_to_merge:
        outfile.write(read_rename_delete(fpath, sname))

print("Géométrie 'box_walls.stl' générée (inlet + outlet + walls).")

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()