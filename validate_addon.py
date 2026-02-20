import json
import os
import sys

ADDON_DIR = "muscular_villager_addon"

def validate_json_syntax(directory):
    print(f"Validating JSON syntax in {directory}...")
    errors = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error in {path}: {e}")
                    errors += 1
    if errors == 0:
        print("All JSON files are valid.")
    else:
        print(f"Found {errors} JSON errors.")
        sys.exit(1)

def validate_manifests():
    print("Validating manifest dependencies...")
    bp_path = os.path.join(ADDON_DIR, "BP", "manifest.json")
    rp_path = os.path.join(ADDON_DIR, "RP", "manifest.json")

    if not os.path.exists(bp_path) or not os.path.exists(rp_path):
        print("Manifest files missing.")
        sys.exit(1)

    with open(bp_path, "r") as f:
        bp = json.load(f)
    with open(rp_path, "r") as f:
        rp = json.load(f)

    bp_uuid = bp["header"]["uuid"]
    rp_uuid = rp["header"]["uuid"]

    # Check BP depends on RP
    bp_deps = [d["uuid"] for d in bp.get("dependencies", []) if "uuid" in d]
    if rp_uuid not in bp_deps:
        print(f"Error: BP does not depend on RP UUID {rp_uuid}")
        sys.exit(1)

    # Check RP depends on BP
    rp_deps = [d["uuid"] for d in rp.get("dependencies", []) if "uuid" in d]
    if bp_uuid not in rp_deps:
        print(f"Error: RP does not depend on BP UUID {bp_uuid}")
        sys.exit(1)

    print("Manifest dependencies are correct.")

def validate_texture_reference():
    print("Validating texture references...")
    # Check if entity json references a texture that exists
    entity_path = os.path.join(ADDON_DIR, "RP", "entity", "muscular_villager.entity.json")
    with open(entity_path, "r") as f:
        data = json.load(f)

    textures = data["minecraft:client_entity"]["description"]["textures"]
    for key, tex_path in textures.items():
        # tex_path is relative to RP root usually, e.g. "textures/entity/muscular_villager"
        # File should be at RP/textures/entity/muscular_villager.png or .tga

        real_path = os.path.join(ADDON_DIR, "RP", tex_path + ".png")
        if not os.path.exists(real_path):
            real_path_tga = os.path.join(ADDON_DIR, "RP", tex_path + ".tga")
            if not os.path.exists(real_path_tga):
                 print(f"Error: Texture {tex_path} not found at {real_path}")
                 sys.exit(1)

    print("Texture references are valid.")

if __name__ == "__main__":
    validate_json_syntax(ADDON_DIR)
    validate_manifests()
    validate_texture_reference()
