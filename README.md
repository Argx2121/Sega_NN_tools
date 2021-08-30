# Sega NN Tools

A Python library for Blender for games using Sega's NN libraries.

## Requirements
 - Blender 2.83 or above.
 - The files you want to import must not be packed.

## Installation
 1. [Download the plugin.](https://github.com/Argx2121/Sega_NN_tools/releases)
 2. Install the addon in blender:
    1. In the top bar: Edit > Preferences
    2. In Preferences: Addons > Install
    3. In Blender File view: Navigate to where you downloaded the zip file, select the file and select Install Add-on.
    4. In Preferences: Check the box for Sega NN tools.
 - On updating you need to install the new version and restart Blender.
 - If downloading a zip from GitHub before release, you'll have to rename the folder from "Sega NN Tools (version number)" to "Sega_NN_tools" inside the zip.

## Usage
1. Open from either
   - 3d view > Sidebar (press n on your keyboard!) > Sega NN tools > import
   - Top bar > file > import 
2. Choose the correct *no format and game that the file originates from.
 - Importing files in batch opens the console on Windows and prints file information while processing files.

## Games
 - With all games files should be extracted. Files without the appropriate file extension (.cno, .eno, lno, etc.) will not be read.
 - All games have a slightly different file format - please specify the game for the tool so it can import the model correctly. If no game is specified the tool may import the model incorrectly.
 - The tool comes with some file extractors. Please use them when applicable. 

## Supported Game Formats

### Cno
#### The House of the Dead 4

### Eno
#### Sonic Free Riders

### Gno
#### Sonic and the Black Knight
#### Sonic Unleashed
#### Sonic Riders Zero Gravity
#### Sonic and the Secret Rings
#### Bleach: Shattered Blade
#### Sonic Riders

### Ino
#### Sonic 4 Episode 1

### Lno
#### The House of the Dead 4
#### Loving Deads: The House of the Dead EX

### Sno
 - Sno file importing is imperfect and may have issues.
#### Sonic Riders Zero Gravity
#### Sega Superstars
#### Sega Ages 2500 Series Vol. 5: Golden Axe

### Uno
#### K-On! After School Live!!

### Xno
#### Sonic Riders
 - Some textures may be pink in blender - this is a known issue that doesn't otherwise influence how the addon functions.
#### Sonic (2006)
#### Phantasy Star Universe

### Zno
#### Sega Golden Gun
#### Sonic 4 Episode 1
#### Transformers: Human Alliance

## About

### Developers
 - Arg!!
 
### Special thanks
 - firegodjr
 - Sewer56
 - Shadowth117
 - Yacker

### Links
[Discord Link](https://discord.gg/CURRBfq) 

[GitHub Link](https://github.com/Argx2121/Sega_NN_tools/)
