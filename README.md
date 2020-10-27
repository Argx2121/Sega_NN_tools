# Sega NN Tools (0.4.0)

A Python library for Blender of tools for games using Sega's NN libraries.

## Requirements
 - Blender 2.80 or above.

## Installation
 1. [Download the plugin](https://github.com/Argx2121/Sega_NN_tools/releases)
 2. Install the addon in blender:
    1. In the top bar: edit > preferences
    2. In Blender preferences: addons > install
    3. In Blender file view: navigate to where you downloaded the zip, select the zip and press install addon.
    4. In Blender preferences: make sure the box for Sega NN tools is checked.
- On updating you should reload scripts by pressing f8 (or spacebar if you've set the search key as it) and searching reload to find the option "Reload scripts"
- If downloading zip from code, you'll have to rename the folder from "Sega NN Tools (0.4.0)" to "Sega_NN_tools" inside the zip

## Usage
1. Open from either
   - 3d view > sidebar (press n on your keyboard!) > Sega NN tools > import
   - Top bar > file > import > Sega NN xno 
2. Choose the correct game format that the model originates from.
3. Importing large files or files in batch opens the console to print data on windows, to show the user that files are being processed.
  
## About

### Developers
 - Arg!!
 
### Special thanks
 - firegodjr
 - Sewer56
 - Shadowth117
 - Yacker
[Discord Link](https://discord.gg/CURRBfq)
[GitHub Link](https://github.com/Argx2121/Sega_NN_tools/)
## Games

### Xno

#### Sonic Riders
- Archive files include both models and textures in them, and textures are exported out of the file so they can be used.
- The Simple / Complex names setting should be simple when handling player models and complex when otherwise.
- The Import Models+ setting is used when importing map files. It is experimental, but it allows you to import collision and other data.
- Some textures may just be pink in blender - this is a known issue that doesn't otherwise influence how the addon functions.

##### Texture swapping
1. Go to 3d view > sidebar > Sega NN tools > Sonic Riders PC Tools > Extract or Insert Textures.
2. Extract all the textures required (if doing player models extract batch with simple names, for maps use complex names.)
3. Replace extracted textures with your own (should have the same filename and be a dds file.)
4. Insert textures.

- Supported formats are: .dds files (dxt1, dxt3 and dxt5 aka bc1, bc1a, bc2 and bc3)
- Texture dimensions should be a power of 2 (2, 4, 8, 16, 32, 64, 128 etc.)
- Riders has a set amount of memory reserved for loaded files - this means files can't be too large. If you make textures 4k you *will* crash the game. To stay safe, you shouldn't stray far from the textures original dimensions. 
- You don't have to replace every file with your own, you just need to have all textures extracted.

#### Sonic (2006)
- Character model vertex colours are not suggested to import as they seem to be unused and distort the models appearance.
- The files are expected to be individualised, that is to say model.xno and texture.dds.
- If there is another way they're usually stored, please let me know!!

#### Phantasy Star Universe
- The importer will only read models if the file starts with "NXOB".
- Some model files may start with a different name which won't be read.

### Zno

#### Sonic 4 Episode 1
- Files have to be extracted from AMBs before they can be used.
- An extractor for that is included for convenience - you may have to run it multiple times as often there are AMBs stored in AMB files. Other external extractors can be used.
- Batch import doesn't use the file extension to determine if it should be read - Unnamed AMB files can be models.