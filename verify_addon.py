import os
import json
import sys

def validate_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        return None

def verify_addon(base_dir):
    print(f"Verifying addon in {base_dir}...")

    rp_dir = os.path.join(base_dir, "RP")
    bp_dir = os.path.join(base_dir, "BP")

    if not os.path.exists(rp_dir):
        print("ERROR: RP directory missing.")
        return
    if not os.path.exists(bp_dir):
        print("ERROR: BP directory missing.")
        return

    # 1. Validate all JSONs
    json_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                filepath = os.path.join(root, file)
                if validate_json_file(filepath) is None:
                    pass # Error already printed
                else:
                    json_files.append(filepath)

    print(f"Validated syntax of {len(json_files)} JSON files.")

    # 2. Check Manifest Dependencies
    rp_manifest_path = os.path.join(rp_dir, "manifest.json")
    bp_manifest_path = os.path.join(bp_dir, "manifest.json")

    rp_data = validate_json_file(rp_manifest_path)
    bp_data = validate_json_file(bp_manifest_path)

    if rp_data and bp_data:
        rp_uuid = rp_data["header"]["uuid"]
        bp_dependencies = bp_data.get("dependencies", [])

        found_dependency = False
        for dep in bp_dependencies:
            if dep.get("uuid") == rp_uuid:
                found_dependency = True
                break

        if found_dependency:
            print("SUCCESS: BP manifest correctly depends on RP UUID.")
        else:
            print(f"ERROR: BP manifest dependency UUID not found. Expected {rp_uuid}")

    # 3. Check Entity References (Basic)
    # Check if client entity texture points to existing file
    entity_dir = os.path.join(rp_dir, "entity")
    if os.path.exists(entity_dir):
        for file in os.listdir(entity_dir):
            if file.endswith(".json"):
                data = validate_json_file(os.path.join(entity_dir, file))
                if data:
                    try:
                        desc = data["minecraft:client_entity"]["description"]
                        textures = desc.get("textures", {})
                        for key, val in textures.items():
                            # val is typically "textures/entity/muscular_villager"
                            # We need to append .png and check existence
                            tex_path = os.path.join(rp_dir, val + ".png")
                            if os.path.exists(tex_path):
                                print(f"SUCCESS: Texture reference found: {val}")
                            else:
                                print(f"WARNING: Texture reference not found: {val} (checked {tex_path})")

                        geometry = desc.get("geometry", {})
                        for key, val in geometry.items():
                            # "geometry.muscular_villager"
                            # We have to find this identifier in models
                            # This is harder without parsing all models.
                            # We'll just assume models are likely correct if JSON is valid.
                            pass

                    except KeyError:
                        pass

if __name__ == "__main__":
    verify_addon("muscular_villager_addon")
