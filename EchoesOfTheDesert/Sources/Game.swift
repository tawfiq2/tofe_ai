import Foundation

/// Regions in the Echoes of the Desert world.
/// These correspond to major biomes inspired by the concept document.
enum Region: String, CaseIterable {
    case emptyQuarter = "Empty Quarter"
    case hijazMountains = "Hijaz Mountains"
    case redSeaCoast = "Red Sea Coast"
    case oasisVillages = "Oases Villages"
}

/// Represents a key character in the narrative.
struct Character {
    let name: String
    let role: String
}

/// A fragment of the ancient seal sought throughout the game.
struct SealFragment {
    let region: Region
    let description: String
    var recovered: Bool = false
}

/// Primary game object modelling a very small slice of the adventure.
class Game {
    let hero: Character
    private(set) var fragments: [SealFragment]

    init(hero: Character, fragments: [SealFragment]) {
        self.hero = hero
        self.fragments = fragments
    }

    /// Mark the fragment from the provided region as recovered.
    func recoverFragment(in region: Region) {
        guard let index = fragments.firstIndex(where: { $0.region == region }) else { return }
        fragments[index].recovered = true
        print("Recovered fragment from \(region.rawValue)")
    }

    /// A basic progress metric for demo purposes.
    func progress() -> Double {
        let total = fragments.count
        let found = fragments.filter { $0.recovered }.count
        return total == 0 ? 0 : Double(found) / Double(total)
    }
}
