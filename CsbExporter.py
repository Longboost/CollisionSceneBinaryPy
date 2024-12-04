from collada import *
import numpy as np
from math import degrees

eff = material.Effect("effect0", [], "phong", diffuse=(1.0, 1.0, 1.0, 1.0), double_sided=False)

def SetupMaterial(attribute: int, flag: int, identifiers: list[int] = None):
    global iomodel, ioscene, eff
    if identifiers is None:
        name = f"MAT{attribute}_FLAG{flag}"
    else:
        #print(identifiers)
        name = f"MAT{attribute}_FLAG{flag}_ID-A{identifiers[0]}_ID-B{identifiers[1]}"
    
    mat = material.Material(name, name, eff)
    matnode = scene.MaterialNode(symbol=name, target=mat, inputs=())
    if not [None for x in ioscene.nodes if type(x) is scene.MaterialNode and x.symbol == matnode.symbol]: # if matnode isn't in nodelist:
        ioscene.nodes.append(matnode)
        iomodel.materials.append(mat)
    return matnode

def SetupMesh(mesh_idx: int, name: str, mat: str, triangles: list, positions: list):
    global iomodel

    vertsrc = positions
    normsrc = []
    idxsrc = []
    
    normidx = 0
    
    for tri in triangles:
        #vertsrc.append(tri.Vertices)
        #print(tri.Vertices)

        idxsrc.append(tri.A)
        idxsrc.append(normidx)
        normidx += 1
        idxsrc.append(tri.B)
        idxsrc.append(normidx)
        normidx += 1
        idxsrc.append(tri.C)
        idxsrc.append(normidx)
        normidx += 1
        normsrc.append(tri.Normal)
        normsrc.append(tri.Normal)
        normsrc.append(tri.Normal)
    vertsrc = source.FloatSource(f"verts-array-{mesh_idx}", np.array(vertsrc).ravel(), ('X', 'Y', 'Z'))
    normsrc = source.FloatSource(f"normals-array-{mesh_idx}", np.array(normsrc).ravel(), ('X', 'Y', 'Z'))
    geom = geometry.Geometry(iomodel, f"{name}_geometry", name, [vertsrc, normsrc])
    
    #print(len(np.array(idxsrc).ravel()))
    idxsrc = np.array(idxsrc)
    input_list = source.InputList()
    input_list.addInput(0, "VERTEX", f"#verts-array-{mesh_idx}")
    input_list.addInput(1, "NORMAL", f"#normals-array-{mesh_idx}")
    
    #print(input_list.getList())
    triset = geom.createTriangleSet(idxsrc, input_list, mat.symbol)
    geom.primitives.append(triset)
    
    geomnode = scene.GeometryNode(geom, [mat])
    
    return geom, geomnode

def LoadNode(node, parent, repeat):
    global currentIdx, node_list, ioscene
    index = node.ID
    #print(currentIdx)
    if not repeat:
        currentIdx += 1
    
    #print(index)
    
    #find the model, mesh or mobj that links to this to label it
    name = f"Node{currentIdx}"
    
    model = next((x for x in csb.Models if x.NodeIndex == index), None)
    
    if not model is None:
        model.AbsoluteIndex = currentIdx - 1
    
    else:
        obj = next((x for x in csb.Objects if x.NodeIndex == index), None)
        
        if not obj is None:
            obj.AbsoluteIndex = currentIdx - 1
        
        elif len(csb.Models[0].Meshes) > 0 :
            mesh = next((x for x in csb.Models[0].Meshes if x.NodeIndex == index), None)
            if not mesh is None:
                mesh.AbsoluteIndex = currentIdx - 1
                name = f"{mesh.Name}"
    
    bone = scene.Node(id=name, children=[])
    
    #if node.NumChildren == -1:
    #    if not repeat:
    #        LoadNode(csb.Nodes[currentIdx-1], bone, True)
    #        LoadNode(csb.Nodes[currentIdx-1], bone, True)
    #        LoadNode(csb.Nodes[currentIdx-1], bone, True)
            
    
    node_list.append(bone)
    
    #print(node.NumChildren)
    if csb.OldParenting:
        startIdx = currentIdx
        while currentIdx < (startIdx + node.NumChildren):
            LoadNode(csb.Nodes[currentIdx], bone, False)
    else:
        for i in range(node.NumChildren):
            LoadNode(csb.Nodes[currentIdx], bone, False)
    
    if parent == None:
        ioscene.nodes.append(bone)
    else:
        parent.children.append(bone)
    
def Export(csb_in, filePath):
    mesh_idx = 0
    
    global csb, node_list, iomodel, ioscene
    csb = csb_in
    ioscene = scene.Scene("scene", [])
    
    iomodel = Collada(validate_output=True)
    
    iomodel.effects.append(eff)
    
    
    #node tree
    
    global currentIdx
    currentIdx = 0
    
    node_list = []
    
    #print([x.Name for x in csb.Nodes])
    #print()
    LoadNode(csb.Nodes[0], None, False)
    
    for obj in csb.Objects:
        type = "MAPOBJ_SPHERE" if obj.IsSphere else "MAPOBJ_BOX"
        
        mat = SetupMaterial(0, obj.ColFlag, [obj.Identifier1, obj.Identifier2])
        
        #Add meshes as map objects
        iomesh, iomeshnode = SetupMesh(mesh_idx, f"{type}_{obj.Name}", mat, [], [])
        mesh_idx += 1

        iomodel.geometries.append(iomesh)
        node_list[obj.AbsoluteIndex].id = obj.Name
        node_list[obj.AbsoluteIndex].name = f'{type}_{obj.Name}'
        node_list[obj.AbsoluteIndex].children.append(iomeshnode)
        node_list[obj.AbsoluteIndex].children.append(scene.TranslateTransform(*obj.Point1))
        node_list[obj.AbsoluteIndex].children.append(scene.RotateTransform(0, 0, 1, degrees(obj.Rotation[2])))
        node_list[obj.AbsoluteIndex].children.append(scene.RotateTransform(0, 1, 0, degrees(obj.Rotation[1])))
        node_list[obj.AbsoluteIndex].children.append(scene.RotateTransform(1, 0, 0, degrees(obj.Rotation[0])))
        node_list[obj.AbsoluteIndex].children.append(scene.ScaleTransform(*obj.Size))
        
        if obj.IsSphere:
            node_list[obj.AbsoluteIndex].children[-1] = scene.ScaleTransform(obj.Radius, obj.Radius, obj.Radius)
    
    for idx, model in enumerate(csb.Models):
        if len(model.Meshes) > 0:
            for mesh in model.Meshes:
                mat = SetupMaterial(mesh.MaterialAttribute, mesh.ColFlag)
                
                iomesh, iomeshnode = SetupMesh(mesh_idx, mesh.Name, mat, mesh.Triangles, mesh.Positions)
                mesh_idx += 1

                iomodel.geometries.append(iomesh)
                node_list[mesh.AbsoluteIndex].children.append(iomeshnode)
        elif len(model.Triangles) > 0:
            mat = SetupMaterial(model.MaterialAttribute, model.ColFlag)
            
            iomesh, iomeshnode = SetupMesh(mesh_idx, model.Name, mat, model.Triangles, model.Positions)
            mesh_idx += 1

            iomodel.geometries.append(iomesh)
            node_list[model.AbsoluteIndex].id = model.Name
            node_list[model.AbsoluteIndex].name = f'MODELSPLIT_{model.Name}'
            node_list[model.AbsoluteIndex].children.append(iomeshnode)
            node_list[model.AbsoluteIndex].children.append(scene.TranslateTransform(*model.Translate))
            node_list[model.AbsoluteIndex].children.append(scene.RotateTransform(0, 0, 1, degrees(model.Rotation[2])))
            node_list[model.AbsoluteIndex].children.append(scene.RotateTransform(0, 1, 0, degrees(model.Rotation[1])))
            node_list[model.AbsoluteIndex].children.append(scene.RotateTransform(1, 0, 0, degrees(model.Rotation[0])))
    iomodel.scenes.append(ioscene)
    iomodel.scene = ioscene
    iomodel.write(filePath)
    # prepend standard dae formatting line
    with open(filePath, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write('<?xml version="1.0" encoding="utf-8"?>'.rstrip('\r\n') + '\n' + content)
    