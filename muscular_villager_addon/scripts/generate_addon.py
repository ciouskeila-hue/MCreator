import json
import os
import uuid
from PIL import Image, ImageDraw

ADDON_NAME = "Muscular Villager Addon"
ADDON_DIR = "muscular_villager_addon"
RP_DIR = os.path.join(ADDON_DIR, "resource_pack")
BP_DIR = os.path.join(ADDON_DIR, "behavior_pack")

# Ensure directories exist
os.makedirs(os.path.join(RP_DIR, "models/entity"), exist_ok=True)
os.makedirs(os.path.join(RP_DIR, "textures/entity/villager"), exist_ok=True)
os.makedirs(os.path.join(RP_DIR, "entity"), exist_ok=True)
os.makedirs(os.path.join(BP_DIR, "entities"), exist_ok=True)

# 1. Geometry (Model)
geometry = {
    "format_version": "1.12.0",
    "minecraft:geometry": [
        {
            "description": {
                "identifier": "geometry.villager_muscle",
                "texture_width": 64,
                "texture_height": 64,
                "visible_bounds_width": 2,
                "visible_bounds_height": 3,
                "visible_bounds_offset": [0, 1.5, 0]
            },
            "bones": [
                { "name": "root", "pivot": [0, 0, 0] },
                { "name": "waist", "parent": "root", "pivot": [0, 12, 0] },
                {
                    "name": "body",
                    "parent": "waist",
                    "pivot": [0, 24, 0],
                    "cubes": [
                        {
                            "origin": [-6, 12, -3],
                            "size": [12, 12, 6],
                            "uv": [16, 20]
                        }
                    ]
                },
                {
                    "name": "head",
                    "parent": "body",
                    "pivot": [0, 24, 0],
                    "cubes": [
                        {
                            "origin": [-4, 24, -4],
                            "size": [8, 10, 8],
                            "uv": [0, 0]
                        },
                        {
                            "origin": [-1, 27, -6],
                            "size": [2, 4, 2],
                            "uv": [24, 0]
                        }
                    ]
                },
                {
                    "name": "leg0",
                    "parent": "waist",
                    "pivot": [-2, 12, 0],
                    "cubes": [
                        {
                            "origin": [-6, 0, -2],
                            "size": [4, 12, 4],
                            "uv": [0, 22]
                        }
                    ]
                },
                {
                    "name": "leg1",
                    "parent": "waist",
                    "pivot": [2, 12, 0],
                    "cubes": [
                        {
                            "origin": [2, 0, -2],
                            "size": [4, 12, 4],
                            "uv": [0, 22],
                            "mirror": True
                        }
                    ]
                },
                {
                    "name": "arm0",
                    "parent": "body",
                    "pivot": [-6, 22, 0],
                    "cubes": [
                        {
                            "origin": [-10, 12, -2],
                            "size": [4, 12, 4],
                            "uv": [40, 22]
                        }
                    ]
                },
                {
                    "name": "arm1",
                    "parent": "body",
                    "pivot": [6, 22, 0],
                    "cubes": [
                        {
                            "origin": [6, 12, -2],
                            "size": [4, 12, 4],
                            "uv": [40, 22],
                            "mirror": True
                        }
                    ]
                }
            ]
        }
    ]
}

with open(os.path.join(RP_DIR, "models/entity/villager_muscle.geo.json"), "w") as f:
    json.dump(geometry, f, indent=2)

# 2. Texture (Image)
img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Colors
SKIN_COLOR = (210, 180, 140, 255)
SHIRT_COLOR = (139, 69, 19, 255) # Brown
PANTS_COLOR = (100, 50, 10, 255) # Darker Brown
NOSE_COLOR = (220, 190, 150, 255)

# Helper to fill rects based on simple logic (not precise UV mapping but enough for visual)
# Head Area (0,0) to (32, 16) approx
draw.rectangle([0, 0, 32, 16], fill=SKIN_COLOR)
# Nose
draw.rectangle([24, 0, 30, 6], fill=NOSE_COLOR)

# Body Area (16, 20) -> The torso texture is usually unwrapped.
# Let's just fill the general regions used by the UVs.
draw.rectangle([16, 20, 52, 40], fill=SHIRT_COLOR)

# Legs Area (0, 22)
draw.rectangle([0, 22, 16, 38], fill=PANTS_COLOR)

# Arms Area (40, 22) -> Skin color for muscles!
draw.rectangle([40, 22, 56, 38], fill=SKIN_COLOR)

# Add some "Muscle Definition" (Lines)
draw.line([42, 22, 42, 38], fill=(180, 150, 110, 255), width=1)
draw.line([44, 25, 52, 25], fill=(180, 150, 110, 255), width=1) # Bicep line?

img.save(os.path.join(RP_DIR, "textures/entity/villager/villager_muscle.png"))

# 3. Manifests
# UUIDs
rp_header_uuid = str(uuid.uuid4())
rp_module_uuid = str(uuid.uuid4())
bp_header_uuid = str(uuid.uuid4())
bp_module_uuid = str(uuid.uuid4())

rp_manifest = {
    "format_version": 2,
    "header": {
        "description": "Resources for Muscular Villager",
        "name": ADDON_NAME + " RP",
        "uuid": rp_header_uuid,
        "version": [1, 0, 0],
        "min_engine_version": [1, 16, 0]
    },
    "modules": [
        {
            "description": "Resource Pack",
            "type": "resources",
            "uuid": rp_module_uuid,
            "version": [1, 0, 0]
        }
    ]
}

bp_manifest = {
    "format_version": 2,
    "header": {
        "description": "Behaviors for Muscular Villager",
        "name": ADDON_NAME + " BP",
        "uuid": bp_header_uuid,
        "version": [1, 0, 0],
        "min_engine_version": [1, 16, 0]
    },
    "modules": [
        {
            "description": "Behavior Pack",
            "type": "data",
            "uuid": bp_module_uuid,
            "version": [1, 0, 0]
        }
    ],
    "dependencies": [
        {
            "uuid": rp_header_uuid,
            "version": [1, 0, 0]
        }
    ]
}

with open(os.path.join(RP_DIR, "manifest.json"), "w") as f:
    json.dump(rp_manifest, f, indent=2)

with open(os.path.join(BP_DIR, "manifest.json"), "w") as f:
    json.dump(bp_manifest, f, indent=2)

# 4. Entity Definitions
# RP Entity Definition (Client side visual)
villager_entity_client = {
    "format_version": "1.10.0",
    "minecraft:client_entity": {
        "description": {
            "identifier": "minecraft:villager_v2",
            "materials": { "default": "entity_alphatest" },
            "textures": { "default": "textures/entity/villager/villager_muscle" },
            "geometry": { "default": "geometry.villager_muscle" },
            "render_controllers": [ "controller.render.villager_v2_base" ]
        }
    }
}

with open(os.path.join(RP_DIR, "entity/villager.entity.json"), "w") as f:
    json.dump(villager_entity_client, f, indent=2)

print("Addon assets generated successfully.")
