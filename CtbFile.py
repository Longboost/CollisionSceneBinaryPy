from CsbFile import CsbFile
import OctreeGenerator

from struct import pack

class CtbFile:
    num_model_groups = 1
    root_size = None #float
    unk = 4.0 #always 4 (TODO: Verify that this is the case for sticker star)
    root_position = [None, None, None] #vec3
    
    class Node:
        position = [None, None, None] #vec3
        size = None #float
        node_id = 0
        child_bits = 0 #bit per octree child, total of 8
        root_flag = 0x7F
        padding = 0xCCCC #int
        num_triangles = None #int
        
        TriangleIndices = None #list[int]
        def __init__(self):
            self.Children = list() #list[Node]
    
    Nodes = list() #list[Node]
    
    def GetTriangles(self, node: OctreeGenerator.OctreeNode):
        if node is None: return list()
        
        indices = []
        indices.extend([x.ID for x in node.Triangles])
        
        for i in range(len(node.Children)):
            indices.extend(self.GetTriangles(node.Children[i]))
        
        return sorted(list(dict.fromkeys(indices)))
    
    def SetupOctree(self, node: OctreeGenerator.OctreeNode, cTreeNode: Node):
        for i in range(len(node.Children)):
            if node.Children[i] is None:
                continue
            
            triangles = self.GetTriangles(node.Children[i])
            if len(triangles) == 0:
                continue
            
            cTreeNode.child_bits |= (1 << i)
            
            c = self.Node()
            
            c.position = node.Children[i].Position
            c.size = node.Children[i].Scale
            c.node_id = i
            c.root_flag = 0xCC
            if node.Children[i].IsLeaf():
                c.node_id = self.id + i
            
            c.TriangleIndices = triangles
            
            c = self.SetupOctree(node.Children[i], c)
            
            cTreeNode.Children.append(c)
        self.id += 8
        return cTreeNode
            
    def GetNodesRecursive(self, node: Node):
        nodes = [node]
        #print(len(node.Children))
        for child in node.Children:
            nodes.extend(self.GetNodesRecursive(child))
        return nodes
    
    def Generate(self, csbFile: CsbFile):
        print('Generating collision table binary')
        
        #CTB only gets used for singular csb model files
        model = csbFile.Models[0]
        # No triangles to search for, skip
        if len(model.Triangles) == 0:
            return
        
        Min = model.Bounding.Min
        Max = model.Bounding.Max
        size = [b - a for a, b in zip(Min, Max)]
        center = [(a + b) / 2 for a, b in zip(Min, Max)]
        
        scale = max(Max[0] - Min[0], Max[2] - Min[2])
        #largest scale halved, but slightly scaled up
        #Unsure how this is really handled. 
        root_scale = scale / 2
        root_position = (center[0], 0, center[2])
        
        octree = OctreeGenerator.Generate(root_position, root_scale, model.Triangles)
        
        root = self.Node()
        root.root_flag = 0xCC
        
        root.TriangleIndices = self.GetTriangles(octree)
        root.position = root_position
        root.size = root_scale
        root.node_id = 1
        
        self.id = 2
        root = self.SetupOctree(octree, root)
        self.Nodes = self.GetNodesRecursive(root)
    
    def Write(self, big_endian: bool = False):
        byteOrder = '>' if big_endian else '<'
        
        writer = bytearray()
        writer.extend(pack(f'{byteOrder}I', 0))
        writer.extend(pack(f'{byteOrder}I', 0))
        writer.extend(pack(f'{byteOrder}I', 0))
        writer.extend(pack(f'{byteOrder}I', self.num_model_groups))
        writer.extend(pack(f'{byteOrder}f', self.Nodes[0].size))
        writer.extend(pack(f'{byteOrder}f', self.unk))
        writer.extend(pack(f'{byteOrder}f', self.Nodes[0].position[0]))
        writer.extend(pack(f'{byteOrder}f', self.Nodes[0].position[1]))
        writer.extend(pack(f'{byteOrder}f', self.Nodes[0].position[2]))
        writer.extend(pack(f'{byteOrder}I', len(self.Nodes)))
        writer.extend(pack(f'{byteOrder}I', len(self.Nodes[0].TriangleIndices)))
        for node in self.Nodes:
            writer.extend(pack(f'{byteOrder}f', node.position[0]))
            writer.extend(pack(f'{byteOrder}f', node.position[1]))
            writer.extend(pack(f'{byteOrder}f', node.position[2]))
            writer.extend(pack(f'{byteOrder}f', node.size))
            writer.extend(pack(f'{byteOrder}I', node.node_id))
            writer.extend(pack(f'{byteOrder}B', node.child_bits))
            writer.extend(pack(f'{byteOrder}B', node.root_flag))
            writer.extend(pack(f'{byteOrder}H', node.padding))
            writer.extend(pack(f'{byteOrder}I', len(node.TriangleIndices)))
        
        for node in self.Nodes:
            for index in node.TriangleIndices:
                writer.extend(pack(f'{byteOrder}I', index))
        
        return writer
    