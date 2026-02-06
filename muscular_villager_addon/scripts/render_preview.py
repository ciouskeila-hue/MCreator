import json
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from PIL import Image

ADDON_DIR = "muscular_villager_addon"
GEO_PATH = os.path.join(ADDON_DIR, "resource_pack/models/entity/villager_muscle.geo.json")
TEX_PATH = os.path.join(ADDON_DIR, "resource_pack/textures/entity/villager/villager_muscle.png")
OUT_PATH = os.path.join(ADDON_DIR, "preview.png")

def get_average_color(texture, uv, size):
    # uv is [u, v] in pixels. size is [w, h, d]
    u, v = uv
    w, h = texture.size
    if u >= w: u = w - 1
    if v >= h: v = h - 1

    # Sample a small patch
    box = (int(u), int(v), int(min(u+4, w)), int(min(v+4, h)))
    try:
        region = texture.crop(box)
        avg = region.resize((1, 1)).getpixel((0, 0))
        return [x/255.0 for x in avg]
    except:
        return [0.5, 0.5, 0.5, 1.0]

def render():
    if not os.path.exists(GEO_PATH):
        print(f"Geometry not found at {GEO_PATH}")
        return
    if not os.path.exists(TEX_PATH):
        print(f"Texture not found at {TEX_PATH}")
        return

    with open(GEO_PATH, 'r') as f:
        geo_data = json.load(f)

    texture = Image.open(TEX_PATH)

    # Setup Figure
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_axis_off() # Hide axes
    ax.set_facecolor('white') # White background
    fig.patch.set_facecolor('white')

    # Parse Geometry
    model = None
    for g in geo_data['minecraft:geometry']:
        if g['description']['identifier'] == 'geometry.villager_muscle':
            model = g
            break

    if not model:
        print("Model identifier not found.")
        return

    bones = model['bones']

    # Calculate bounds to center the camera
    min_x, max_x = 0, 0
    min_y, max_y = 0, 0
    min_z, max_z = 0, 0

    polys = []

    for bone in bones:
        if 'cubes' not in bone:
            continue

        # Bone pivot can affect rotation but for simple villager model
        # usually cubes are positioned absolutely or relative to pivot which is 0-based in some contexts.
        # Bedrock geometry is tricky. The "origin" is usually absolute in model space.
        # We will assume origin is absolute for this visualization.

        for cube in bone['cubes']:
            origin = cube['origin'] # [x, y, z]
            size = cube['size']     # [w, h, d]
            uv = cube.get('uv', [0, 0])

            x, y, z = origin
            dx, dy, dz = size

            # Update bounds
            min_x = min(min_x, x)
            max_x = max(max_x, x + dx)
            min_y = min(min_y, y)
            max_y = max(max_y, y + dy)
            min_z = min(min_z, z)
            max_z = max(max_z, z + dz)

            # Matplotlib Coords:
            # Bedrock: X=Right, Y=Up, Z=Forward (North)
            # Matplotlib: X, Y, Z. usually Z is up.
            # So Bedrock X -> Plot X
            # Bedrock Y -> Plot Z
            # Bedrock Z -> Plot Y

            # Corner points
            p = [
                [x, z, y],
                [x+dx, z, y],
                [x+dx, z+dz, y],
                [x, z+dz, y],
                [x, z, y+dy],
                [x+dx, z, y+dy],
                [x+dx, z+dz, y+dy],
                [x, z+dz, y+dy]
            ]

            # Faces
            faces = [
                [p[0], p[1], p[2], p[3]], # Bottom
                [p[4], p[5], p[6], p[7]], # Top
                [p[0], p[1], p[5], p[4]], # Front
                [p[2], p[3], p[7], p[6]], # Back
                [p[1], p[2], p[6], p[5]], # Right
                [p[4], p[7], p[3], p[0]]  # Left
            ]

            color = get_average_color(texture, uv, size)

            # Alpha 1.0 for solid look
            poly3d = Poly3DCollection(faces, linewidths=0.5, edgecolors='none', alpha=1.0)
            poly3d.set_facecolor(color)
            poly3d.set_edgecolor(color) # Hide edges by making them same color
            polys.append(poly3d)
            ax.add_collection3d(poly3d)

    # Set limits centered on the model
    center_x = (min_x + max_x) / 2
    center_y = (min_z + max_z) / 2 # Bedrock Z is Plot Y
    center_z = (min_y + max_y) / 2 # Bedrock Y is Plot Z

    max_range = max(max_x - min_x, max_z - min_z, max_y - min_y) / 2

    ax.set_xlim(center_x - max_range, center_x + max_range)
    ax.set_ylim(center_y - max_range, center_y + max_range)
    ax.set_zlim(center_z - max_range, center_z + max_range)

    # Isometric view
    ax.view_init(elev=30, azim=-45)

    # Save
    plt.savefig(OUT_PATH, bbox_inches='tight', pad_inches=0.1, dpi=150)
    print(f"Preview saved to {OUT_PATH}")

if __name__ == "__main__":
    render()
