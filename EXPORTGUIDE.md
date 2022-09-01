# Sega NN Tools Export Guide
Please note that this only works on Windows devices!

## Table of Contents
[Introduction](#Introduction)

[Bones](#Bones)

[Materials](#Materials)

[Meshes](#Meshes)

[Prepare Model](#Prepare-Model)


## Introduction
This is a guide for making custom models to be exported in a Sega NN model file format. 
There are some restrictions and naming requirements that need to be followed to ensure the model is exported as you would expect it to.

Please make sure to select the right game as every game stores model data differently.
## Bones
If you are model swapping you want to keep the same bone count, bone hierarchy (bone parents and children) and bone rotation.
Changing rotation or hierarchy will break animations and changing the bone count will crash your game.
You can however, change the bone positions. (Special thanks to Sewer56 for the code that allows bone calculation.)
Please contact me if you export any models and the bones seem to have exported wrong. 
Some models have bones that are stored incorrectly natively due to animations, and the exporter can't write bones that way 
(as it has no way to tell the bone needs to be stored wrong)

## Meshes
Vertex colour and uv maps are supported. Static and Pliable meshes are also supported 
(but should be separate objects - see model preparation.)
You should apply mesh modifiers before you go to export them (mirror, subdivide, etc.) 
You'll also want them to be triangulated.

## Materials
NN only allows for one material per mesh. 
If you want textures on the model, you need to follow these naming conventions for the texture node:

Diffuse texture (texture that puts colour on the mesh): "DiffuseTexture"

Reflection texture (texture that makes the mesh look reflective): "ReflectionTexture"

Emission texture (texture that allows the mesh to emit light): "EmissionTexture"

You set the node name in the shader tab by selecting the texture node and opening the node tab.

## Prepare Model
Please run this function after you have made your model, before exporting it.

This function splits meshes into selections that NN can handle (static and pliable)
based on the games requirements. If you do not run this you may get models exporting with incorrect weights or game crashes.

After running this feel free to export with the correct game settings.