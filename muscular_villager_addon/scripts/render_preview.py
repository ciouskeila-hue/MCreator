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
    # In bedrock, box UV mapping is complex (unfolding).
    # We will just sample a patch at uv[0], uv[1] of size roughly representative.
    # UV in JSON is usually top-left of the texture box.
    u, v = uv
    # Ensure bounds
    w, h = texture.size
    if u >= w: u = w - 1
    if v >= h: v = h - 1

    # Sample a 4x4 patch or smaller
    box = (int(u), int(v), int(min(u+4, w)), int(min(v+4, h)))
    try:
        region = texture.crop(box)
        # resize to 1x1 to get average
        avg = region.resize((1, 1)).getpixel((0, 0))
        return [x/255.0 for x in avg] # Normalize to 0-1
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

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Parse Geometry
    # Looking for geometry.villager_muscle
    model = None
    for g in geo_data['minecraft:geometry']:
        if g['description']['identifier'] == 'geometry.villager_muscle':
            model = g
            break

    if not model:
        print("Model identifier not found.")
        return

    bones = model['bones']

    # Store cubes to plot
    # A cube is defined by origin and size.

    # Set plot limits
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20) # Z in bedrock
    ax.set_zlim(0, 40)   # Y in bedrock

    ax.set_xlabel('X')
    ax.set_ylabel('Z (Bedrock Z)')
    ax.set_zlabel('Y (Bedrock Y)')

    for bone in bones:
        if 'cubes' not in bone:
            continue

        for cube in bone['cubes']:
            origin = cube['origin'] # [x, y, z]
            size = cube['size']     # [w, h, d]
            uv = cube.get('uv', [0, 0])

            x, y, z = origin
            dx, dy, dz = size

            # Matplotlib coordinates setup
            # We map Bedrock [x, y, z] to Matplotlib axes.
            # Usually Matplotlib Z is height. So Bedrock Y -> Plot Z.
            # Bedrock Z -> Plot Y.

            # Vertices of the cube
            # origin is bottom-north-west (roughly)

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

            # Faces defined by indices
            faces = [
                [p[0], p[1], p[2], p[3]], # Bottom
                [p[4], p[5], p[6], p[7]], # Top
                [p[0], p[1], p[5], p[4]], # Front (ish)
                [p[2], p[3], p[7], p[6]], # Back
                [p[1], p[2], p[6], p[5]], # Right
                [p[4], p[7], p[3], p[0]]  # Left
            ]

            color = get_average_color(texture, uv, size)

            poly3d = Poly3DCollection(faces, linewidths=1, edgecolors='k', alpha=0.9)
            poly3d.set_facecolor(color)
            ax.add_collection3d(poly3d)

    # Adjust view
    ax.view_init(elev=20, azim=45)

    plt.savefig(OUT_PATH)
    print(f"Preview saved to {OUT_PATH}")

if __name__ == "__main__":
    render()
