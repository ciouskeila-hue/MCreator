import json
import os
import uuid
from PIL import Image, ImageDraw

# Configuration
ADDON_NAME = "Muscular Villager"
ADDON_ID = "muscular_villager"
NAMESPACE = "my"
BP_UUID = str(uuid.uuid4())
RP_UUID = str(uuid.uuid4())
BP_MODULE_UUID = str(uuid.uuid4())
RP_MODULE_UUID = str(uuid.uuid4())
SCRIPT_MODULE_UUID = str(uuid.uuid4())

# Paths
ROOT = "muscular_villager_addon"
BP = os.path.join(ROOT, "BP")
RP = os.path.join(ROOT, "RP")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_manifest_bp():
    manifest = {
        "format_version": 2,
        "header": {
            "name": f"{ADDON_NAME} BP",
            "description": "Behavior Pack for Muscular Villager",
            "uuid": BP_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "data",
                "uuid": BP_MODULE_UUID,
                "version": [1, 0, 0]
            },
            {
                "type": "script",
                "language": "javascript",
                "uuid": SCRIPT_MODULE_UUID,
                "entry": "scripts/server/index.js",
                "version": [1, 0, 0]
            }
        ],
        "dependencies": [
            {
                "uuid": RP_UUID,
                "version": [1, 0, 0]
            },
            {
                "module_name": "@minecraft/server",
                "version": "1.10.0"
            }
        ]
    }
    with open(os.path.join(BP, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)

def create_manifest_rp():
    manifest = {
        "format_version": 2,
        "header": {
            "name": f"{ADDON_NAME} RP",
            "description": "Resource Pack for Muscular Villager",
            "uuid": RP_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0]
        },
        "modules": [
            {
                "type": "resources",
                "uuid": RP_MODULE_UUID,
                "version": [1, 0, 0]
            }
        ],
        "dependencies": [
            {
                "uuid": BP_UUID,
                "version": [1, 0, 0]
            }
        ]
    }
    with open(os.path.join(RP, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=4)

def create_geometry():
    # A simple geometry with a body, head, and thick arms
    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": f"geometry.{ADDON_ID}",
                    "texture_width": 64,
                    "texture_height": 64,
                    "visible_bounds_width": 2,
                    "visible_bounds_height": 3,
                    "visible_bounds_offset": [0, 1.5, 0]
                },
                "bones": [
                    {
                        "name": "root",
                        "pivot": [0, 0, 0]
                    },
                    {
                        "name": "waist",
                        "parent": "root",
                        "pivot": [0, 12, 0]
                    },
                    {
                        "name": "body",
                        "parent": "waist",
                        "pivot": [0, 24, 0],
                        "cubes": [
                            {"origin": [-4, 12, -2], "size": [8, 12, 4], "uv": [16, 16]}
                        ]
                    },
                    {
                        "name": "head",
                        "parent": "body",
                        "pivot": [0, 24, 0],
                        "cubes": [
                            {"origin": [-4, 24, -4], "size": [8, 10, 8], "uv": [0, 0]}
                        ]
                    },
                    {
                        "name": "leftArm",
                        "parent": "body",
                        "pivot": [5, 22, 0],
                        "cubes": [
                            {"origin": [4, 12, -2], "size": [6, 12, 6], "uv": [40, 16]}
                        ]
                    },
                    {
                        "name": "rightArm",
                        "parent": "body",
                        "pivot": [-5, 22, 0],
                        "cubes": [
                            {"origin": [-10, 12, -2], "size": [6, 12, 6], "uv": [40, 16]}
                        ]
                    },
                    {
                        "name": "leftLeg",
                        "parent": "root",
                        "pivot": [2, 12, 0],
                        "cubes": [
                            {"origin": [0, 0, -2], "size": [4, 12, 4], "uv": [0, 16]}
                        ]
                    },
                    {
                        "name": "rightLeg",
                        "parent": "root",
                        "pivot": [-2, 12, 0],
                        "cubes": [
                            {"origin": [-4, 0, -2], "size": [4, 12, 4], "uv": [0, 16]}
                        ]
                    }
                ]
            }
        ]
    }
    with open(os.path.join(RP, f"models/entity/{ADDON_ID}.geo.json"), "w") as f:
        json.dump(geo, f, indent=4)

def create_texture():
    # Create a 64x64 texture
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fill background (transparent)

    # Head (0,0) 8x8x8 -> 32x16 area
    draw.rectangle([0, 0, 32, 16], fill=(236, 188, 180, 255)) # Skin color
    # Face details
    draw.rectangle([4, 4, 6, 6], fill=(0, 0, 0, 255)) # Eye L
    draw.rectangle([10, 4, 12, 6], fill=(0, 0, 0, 255)) # Eye R

    # Body (16,16) 8x12x4
    draw.rectangle([16, 16, 40, 32], fill=(100, 50, 50, 255)) # Shirt

    # Arms (40, 16) 4x12x4 (thicker)
    draw.rectangle([40, 16, 64, 32], fill=(236, 188, 180, 255)) # Skin arms

    # Legs (0, 16) 4x12x4
    draw.rectangle([0, 16, 16, 32], fill=(50, 50, 100, 255)) # Pants

    img.save(os.path.join(RP, f"textures/entity/{ADDON_ID}.png"))

def create_animation():
    anim = {
        "format_version": "1.8.0",
        "animations": {
            f"animation.{ADDON_ID}.idle": {
                "loop": True,
                "bones": {
                    "head": {
                        "rotation": ["math.sin(query.life_time * 20) * 5", 0, 0]
                    },
                    "leftArm": {
                        "rotation": [0, 0, -5]
                    },
                    "rightArm": {
                        "rotation": [0, 0, 5]
                    }
                }
            },
            f"animation.{ADDON_ID}.walk": {
                "loop": True,
                "anim_time_update": "query.modified_distance_moved",
                "bones": {
                    "leftLeg": {
                        "rotation": ["math.sin(query.anim_time * 20) * 20", 0, 0]
                    },
                    "rightLeg": {
                        "rotation": ["math.sin(query.anim_time * 20 + 180) * 20", 0, 0]
                    },
                    "leftArm": {
                        "rotation": ["math.sin(query.anim_time * 20 + 180) * 20", 0, 0]
                    },
                    "rightArm": {
                        "rotation": ["math.sin(query.anim_time * 20) * 20", 0, 0]
                    }
                }
            },
            f"animation.{ADDON_ID}.throw": {
                "loop": "hold_on_last_frame",
                "animation_length": 1.0,
                "bones": {
                    "body": {
                        "rotation": {
                            "0.0": [0, 0, 0],
                            "0.5": [-20, 0, 0],
                            "0.8": [45, 0, 0],
                            "1.0": [0, 0, 0]
                        }
                    },
                    "leftArm": {
                        "rotation": {
                            "0.0": [0, 0, 0],
                            "0.5": [-160, 0, 0],
                            "0.8": [45, 0, 0]
                        }
                    },
                    "rightArm": {
                         "rotation": {
                            "0.0": [0, 0, 0],
                            "0.5": [-160, 0, 0],
                            "0.8": [45, 0, 0]
                        }
                    }
                }
            }
        }
    }
    with open(os.path.join(RP, f"animations/{ADDON_ID}.animation.json"), "w") as f:
        json.dump(anim, f, indent=4)

def create_render_controller():
    rc = {
        "format_version": "1.8.0",
        "render_controllers": {
            f"controller.render.{ADDON_ID}": {
                "geometry": f"Geometry.default",
                "materials": [ { "*": "Material.default" } ],
                "textures": [ "Texture.default" ]
            }
        }
    }
    with open(os.path.join(RP, f"render_controllers/{ADDON_ID}.render_controllers.json"), "w") as f:
        json.dump(rc, f, indent=4)

def create_client_entity():
    ce = {
        "format_version": "1.10.0",
        "minecraft:client_entity": {
            "description": {
                "identifier": f"{NAMESPACE}:{ADDON_ID}",
                "materials": {
                    "default": "entity_alphatest"
                },
                "textures": {
                    "default": f"textures/entity/{ADDON_ID}"
                },
                "geometry": {
                    "default": f"geometry.{ADDON_ID}"
                },
                "scripts": {
                    "animate": [
                        "idle_anim",
                        {"walk_anim": "query.modified_move_speed > 0.1"},
                        {"throw_anim": "query.variant == 1"}
                    ]
                },
                "animations": {
                    "idle_anim": f"animation.{ADDON_ID}.idle",
                    "walk_anim": f"animation.{ADDON_ID}.walk",
                    "throw_anim": f"animation.{ADDON_ID}.throw"
                },
                "render_controllers": [ f"controller.render.{ADDON_ID}" ]
            }
        }
    }
    with open(os.path.join(RP, f"entity/{ADDON_ID}.entity.json"), "w") as f:
        json.dump(ce, f, indent=4)

def create_server_entity():
    se = {
        "format_version": "1.19.0",
        "minecraft:entity": {
            "description": {
                "identifier": f"{NAMESPACE}:{ADDON_ID}",
                "is_spawnable": True,
                "is_summonable": True,
                "is_experimental": False
            },
            "component_groups": {
                "my:throwing": {
                     "minecraft:variant": {"value": 1}
                },
                "my:idle": {
                     "minecraft:variant": {"value": 0}
                }
            },
            "components": {
                "minecraft:type_family": ["villager", "mob"],
                "minecraft:health": {
                    "value": 100,
                    "max": 100
                },
                "minecraft:collision_box": {
                    "width": 0.6,
                    "height": 1.9
                },
                "minecraft:movement": {
                    "value": 0.3
                },
                "minecraft:movement.basic": {},
                "minecraft:navigation.walk": {
                    "can_path_over_water": True
                },
                "minecraft:behavior.random_stroll": {
                    "priority": 6,
                    "speed_multiplier": 1.0
                },
                "minecraft:behavior.look_at_player": {
                    "priority": 7,
                    "look_distance": 6.0,
                    "probability": 0.02
                },
                "minecraft:physics": {},
                "minecraft:pushable": {
                    "is_pushable": True,
                    "is_pushable_by_piston": True
                },
                "minecraft:interact": {
                     "interactions": [
                        {
                            "on_interact": {
                                "filters": { "test": "is_family", "subject": "other", "value": "player" },
                                "event": "my:on_trade"
                            },
                            "use_item": False,
                            "swing": True
                        }
                    ]
                },
                "minecraft:rideable": {
                    "seat_count": 1,
                    "family_types": ["player"],
                    "seats": [
                        {
                            "position": [0.0, 2.2, 0.0],
                            "min_rider_count": 0,
                            "max_rider_count": 1,
                            "lock_rider_rotation": 0
                        }
                    ]
                }
            },
            "events": {
                "my:start_throw": {
                    "add": { "component_groups": ["my:throwing"] },
                    "remove": { "component_groups": ["my:idle"] }
                },
                "my:stop_throw": {
                    "add": { "component_groups": ["my:idle"] },
                    "remove": { "component_groups": ["my:throwing"] }
                },
                "my:on_trade": {
                    "trigger": "my:start_throw"
                }
            }
        }
    }
    with open(os.path.join(BP, f"entities/{ADDON_ID}.json"), "w") as f:
        json.dump(se, f, indent=4)

def create_script():
    js_content = """
import { world, system } from "@minecraft/server";

const ADDON_ID = "my:muscular_villager";

world.afterEvents.entityHitEntity.subscribe((event) => {
    const target = event.hitEntity;
    const attacker = event.damagingEntity;

    if (target && target.typeId === ADDON_ID && attacker && attacker.typeId === "minecraft:player") {
        startThrowSequence(target, attacker);
    }
});

world.afterEvents.playerInteractWithEntity.subscribe((event) => {
    const target = event.target;
    const player = event.player;

    if (target.typeId === ADDON_ID) {
        // Assume interaction means trade/trigger
        startThrowSequence(target, player);
    }
});

function startThrowSequence(villager, player) {
    // Trigger animation via event
    villager.triggerEvent("my:start_throw");

    villager.runCommandAsync(`ride "${player.name}" start_riding @s`).then(() => {
        world.sendMessage("Picked up player!");

        // 2. Wait 2 seconds then throw
        system.runTimeout(() => {
            // Throw logic
            // Stop riding
            villager.runCommandAsync(`ride "${player.name}" stop_riding`).then(() => {
                 // Apply knockback to player
                 const viewDir = villager.getViewDirection();
                 const strength = 5;
                 player.applyKnockback(viewDir.x * strength, viewDir.z * strength, strength, 1.0);
                 world.sendMessage("Yeet!");

                 // Stop animation
                 villager.triggerEvent("my:stop_throw");
            });
        }, 40); // 40 ticks = 2 seconds

    }).catch((e) => {
        world.sendMessage("Failed to pick up: " + e);
        villager.triggerEvent("my:stop_throw");
    });
}

"""
    with open(os.path.join(BP, "scripts/server/index.js"), "w") as f:
        f.write(js_content)

def main():
    print("Generating addon files...")
    create_manifest_bp()
    create_manifest_rp()
    create_geometry()
    create_texture()
    create_animation()
    create_render_controller()
    create_client_entity()
    create_server_entity()
    create_script()
    print("Done.")

if __name__ == "__main__":
    main()
