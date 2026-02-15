import { world, system } from "@minecraft/server";

// Constants
const VILLAGER_ID = "custom:muscular_villager";

// Event: Player Attacks Villager
world.afterEvents.entityHitEntity.subscribe((ev) => {
    const { damagingEntity, hitEntity } = ev;
    if (!damagingEntity || !hitEntity) return;

    if (hitEntity.typeId === VILLAGER_ID && damagingEntity.typeId === "minecraft:player") {
        liftPlayer(damagingEntity, hitEntity);
    }
});

// Event: Player Interacts with Villager
world.afterEvents.playerInteractWithEntity.subscribe((ev) => {
    const { player, target } = ev;
    if (!player || !target) return;

    if (target.typeId === VILLAGER_ID) {
        liftPlayer(player, target);
    }
});

function liftPlayer(player, villager) {
    if (!player.isValid() || !villager.isValid()) return;

    // Check if villager already has a rider
    const rideable = villager.getComponent("minecraft:rideable");
    if (!rideable) return;

    const riders = rideable.getRiders();
    if (riders && riders.length > 0) {
        // Already holding someone
        return;
    }

    // Log interaction
    world.sendMessage("Lifting player: " + player.name);

    // Attempt to mount
    try {
        const success = player.startRiding(villager);
        if (success) {
            // Schedule the throw after 3 seconds (60 ticks)
            system.runTimeout(() => {
                throwPlayer(player, villager);
            }, 60);
        }
    } catch (e) {
        console.warn("Failed to start riding: " + e);
    }
}

function throwPlayer(player, villager) {
    // Check validity again as entities might have despawned/died
    if (!player.isValid() || !villager.isValid()) return;

    // Dismount
    player.stopRiding();

    // Log interaction
    world.sendMessage("Throwing player!");

    // Calculate throw direction (Villager's forward direction)
    const viewDir = villager.getViewDirection();

    // Apply Knockback
    try {
         player.applyKnockback(viewDir.x, viewDir.z, 5.0, 1.0);
    } catch (e) {
        console.warn("Failed to apply knockback: " + e);
    }
}
