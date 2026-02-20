
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
