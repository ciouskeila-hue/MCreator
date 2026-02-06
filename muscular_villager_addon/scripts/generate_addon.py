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

# 1. Geometry (Model) - Enhanced
# Villager base scale is roughly 1 pixel = 1/16 meter.
# Height ~ 24 + 10 = 34 pixels ~ 2 meters.

# We will make him buff:
# - Broader shoulders
# - Tapered waist
# - Thicker arms
# - Defined Chest

geometry = {
    "format_version": "1.12.0",
    "minecraft:geometry": [
        {
            "description": {
                "identifier": "geometry.villager_muscle",
                "texture_width": 64,
                "texture_height": 64,
                "visible_bounds_width": 3,
                "visible_bounds_height": 3,
                "visible_bounds_offset": [0, 1.5, 0]
            },
            "bones": [
                { "name": "root", "pivot": [0, 0, 0] },
                { "name": "waist", "parent": "root", "pivot": [0, 12, 0] },

                # BODY
                {
                    "name": "body",
                    "parent": "waist",
                    "pivot": [0, 24, 0],
                    "cubes": [
                        # Torso (Upper Body) - Broad
                        {
                            "origin": [-5, 18, -3],
                            "size": [10, 6, 6],
                            "uv": [16, 20]
                        },
                        # Abs/Lower Torso - Tapered
                        {
                            "origin": [-4, 12, -2.5],
                            "size": [8, 6, 5],
                            "uv": [16, 32]
                        }
                    ]
                },

                # PECS (Added as separate cubes for definition if needed, or part of texture)
                # Let's add slight depth for Pecs
                {
                    "name": "pecs",
                    "parent": "body",
                    "pivot": [0, 24, 0],
                    "cubes": [
                         {
                            "origin": [-4.5, 19, -3.5],
                            "size": [9, 4, 1],
                            "uv": [20, 34]
                        }
                    ]
                },

                # HEAD
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
                        # Nose
                        {
                            "origin": [-1, 27, -6],
                            "size": [2, 4, 2],
                            "uv": [24, 0]
                        }
                    ]
                },

                # LEGS
                {
                    "name": "leg0",
                    "parent": "waist",
                    "pivot": [-2, 12, 0],
                    "cubes": [
                        {
                            "origin": [-4.1, 0, -2],
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
                            "origin": [0.1, 0, -2],
                            "size": [4, 12, 4],
                            "uv": [0, 22],
                            "mirror": True
                        }
                    ]
                },

                # ARMS - BUFF
                {
                    "name": "arm0",
                    "parent": "body",
                    "pivot": [-5, 22, 0],
                    "cubes": [
                        # Shoulder/Deltoid
                        {
                            "origin": [-9, 20, -2.5],
                            "size": [5, 5, 5],
                            "uv": [40, 38]
                        },
                        # Bicep/Arm
                        {
                            "origin": [-8.5, 12, -2],
                            "size": [4, 8, 4],
                            "uv": [40, 22]
                        }
                    ]
                },
                {
                    "name": "arm1",
                    "parent": "body",
                    "pivot": [5, 22, 0],
                    "cubes": [
                         # Shoulder/Deltoid
                        {
                            "origin": [4, 20, -2.5],
                            "size": [5, 5, 5],
                            "uv": [40, 38],
                            "mirror": True
                        },
                        # Bicep/Arm
                        {
                            "origin": [4.5, 12, -2],
                            "size": [4, 8, 4],
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

# 2. Texture (Image) - Enhanced
img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Palette
SKIN_BASE = (189, 139, 114, 255)
SKIN_SHADE = (160, 110, 90, 255)
ROBE_COLOR = (103, 76, 56, 255) # Classic brown
ROBE_DARK = (80, 50, 30, 255)
PANTS_COLOR = (60, 40, 20, 255)
EYE_COLOR = (24, 128, 24, 255) # Green
EYE_WHITE = (255, 255, 255, 255)
BROW_COLOR = (70, 40, 10, 255)

# --- HEAD (0,0, 32, 16) ---
# Fill Base
draw.rectangle([0, 0, 32, 16], fill=SKIN_BASE)
# Eyes
draw.rectangle([8, 10, 9, 11], fill=EYE_WHITE)
draw.rectangle([9, 10, 10, 11], fill=EYE_COLOR)
draw.rectangle([22, 10, 23, 11], fill=EYE_WHITE) # Mirrored ish
draw.rectangle([21, 10, 22, 11], fill=EYE_COLOR)
# Unibrow
draw.rectangle([8, 9, 24, 10], fill=BROW_COLOR)
# Nose (24, 0, 30, 6)
draw.rectangle([24, 0, 30, 6], fill=SKIN_SHADE)

# --- BODY (16, 20) ---
# Upper Body (Broad)
draw.rectangle([16, 20, 26, 26], fill=ROBE_COLOR) # Front
draw.rectangle([26, 20, 36, 26], fill=ROBE_DARK)  # Back
# Abs/Lower Body
draw.rectangle([16, 32, 24, 38], fill=ROBE_COLOR)

# --- PECS (20, 34) ---
# Just skin/muscle definition
draw.rectangle([20, 34, 29, 38], fill=ROBE_DARK) # Shadowy pecs on robe

# --- LEGS (0, 22) ---
draw.rectangle([0, 22, 16, 38], fill=PANTS_COLOR)

# --- ARMS (40, 22) ---
# Arms are exposed muscle
draw.rectangle([40, 22, 56, 38], fill=SKIN_BASE)
# Muscle shading (striations)
for y in range(22, 38, 2):
    draw.line([40, y, 56, y], fill=SKIN_SHADE, width=1)

# Shoulders (40, 38)
draw.rectangle([40, 38, 56, 50], fill=SKIN_BASE)
draw.ellipse([42, 40, 54, 48], outline=SKIN_SHADE) # Deltoid definition

img.save(os.path.join(RP_DIR, "textures/entity/villager/villager_muscle.png"))

# 3. Manifests
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

print("Enhanced Addon assets generated successfully.")
