import Foundation

// Build the hero and initial fragments based on the concept overview.
let hero = Character(name: "Namir", role: "Wanderer")
let fragments = [
    SealFragment(region: .emptyQuarter, description: "A shard buried beneath shifting dunes"),
    SealFragment(region: .hijazMountains, description: "A fragment hidden in a mountain monastery"),
    SealFragment(region: .redSeaCoast, description: "A barnacled piece found by pearl divers"),
    SealFragment(region: .oasisVillages, description: "A relic safeguarded by desert tribes"),
]

var game = Game(hero: hero, fragments: fragments)

// Demo playthrough that recovers two fragments and prints progress.
game.recoverFragment(in: .emptyQuarter)
game.recoverFragment(in: .oasisVillages)
let progress = Int(game.progress() * 100)
print("Current progress: \(progress)% of the seal recovered")
