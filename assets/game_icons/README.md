# Game Icons Directory

This directory contains game-specific icons that are displayed in the Game Status Panel.

## File Naming Convention

Icons should be named using the following format:
- Convert game name to lowercase
- Replace spaces with underscores
- Remove colons and special characters
- Use `.png` or `.jpg` extension

### Examples

| Game Name | Icon Filename |
|-----------|---------------|
| League of Legends | `league_of_legends.png` |
| Counter-Strike 2 | `counter-strike_2.png` |
| Elden Ring | `elden_ring.png` |
| Dark Souls III | `dark_souls_iii.png` |
| Baldur's Gate 3 | `baldurs_gate_3.png` |
| Cyberpunk 2077 | `cyberpunk_2077.png` |
| World of Warcraft | `world_of_warcraft.png` |
| Valorant | `valorant.png` |
| Dota 2 | `dota_2.png` |
| Minecraft | `minecraft.png` |
| Fortnite | `fortnite.png` |
| PUBG | `pubg.png` |
| GTA V | `gta_v.png` |

## Icon Specifications

- **Recommended Size**: 256x256 pixels or larger
- **Format**: PNG (with transparency) or JPG
- **Aspect Ratio**: Square (1:1) works best
- **Background**: Transparent or game-themed

## Fallback Behavior

If no custom icon is found for a game, the application will display the default Omnix logo.

## Adding New Icons

1. Find or create a high-quality icon for the game
2. Name it according to the convention above
3. Place it in this directory (`assets/game_icons/`)
4. The application will automatically detect and use it

## Icon Sources

You can obtain game icons from:
- Official game websites
- Steam store pages
- Game publisher resources
- Community wikis (ensure proper licensing)

**Note**: Ensure you have the right to use any icons you add. Icons are typically trademarked by their respective game publishers.
