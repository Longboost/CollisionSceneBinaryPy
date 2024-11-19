# CollisionSceneBinaryPy
Based majorly off of https://github.com/KillzXGaming/CollisionSceneBinary – credits to KillzXGaming for their .csb tool that is for other Paper Mario entries _(lots of this code is just theirs ported to Python!)_

Exports Paper Mario: Sticker Star's .csb files to a workable .dae file, and allows that file to be reimported with appropiate octree data in a .ctb file. 

**Usage:**

- To export to .dae:
  `main.py <filname>.csb`

- To import back into .csb and generate an associated .ctb:
  `main.py <filname>.dae`

**Side Note:** 

All meshes in the .dae file must be parented to a root mesh (it is typical convention to name this root mesh "A")
