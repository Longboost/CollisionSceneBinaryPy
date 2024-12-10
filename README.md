# CollisionSceneBinaryPy
Based majorly off of https://github.com/KillzXGaming/CollisionSceneBinary – credits to KillzXGaming for their .csb tool that is for other Paper Mario entries _(lots of this code is just theirs ported to Python!)_

Exports Paper Mario: Sticker Star's .csb files to a workable .dae file, and allows that file to be reimported with appropiate octree data in a .ctb file. 

**Setup:**

- You will need [Python](https://www.python.org/) installed
- To install this program's dependencies, run: `pip install -r requirements.txt`

**Usage:**

- To export to .dae:
  `main.py <filename>.csb`

- To import back into .csb and generate an associated .ctb:
  `main.py <filename>.dae`

**Side Note:** 


While it is typical convention to parent all meshes to a root mesh named "A," it is not necessary for the collision model to work.