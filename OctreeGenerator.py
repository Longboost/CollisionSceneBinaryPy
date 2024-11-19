from Triangle import *
import TriangleHelper

class OctreeNode:
    Triangles = list() #list[Triangle]
    
    Children = list() #list[OctreeNode]
    
    def IsLeaf(self) -> bool:
        return bool(self.Children)
    
    def __init__(self, pos: list[float], scale: list[float]):
        self.Position = pos #vec3
        self.Scale = scale #float
        
        self.Triangles = list()
        self.Children = list()
    
    def GetChildOffset(self, index: int) -> list[int]:
        return [
                -1 if (index & 1) == 0 else 1,
                0, #ignore Y
                -1 if (index & 2) == 0 else 1
                ]
    
    # Subdivide the node into eight children
    def Subdivide(self, depth: int):
        #8 octrees can be loaded, but we only load 4 for now
        #Other 4 are used for height, but generally only 4 ever need to be used
        self.Children = [None for _ in range(4)]
        
        childScale = self.Scale / 2
        for i in range(len(self.Children)):
            childPosition = [a + b * childScale for a, b in zip(self.Position, self.GetChildOffset(i))]
            self.Children[i] = OctreeNode(childPosition, childScale)

class Octree:
    root = None # OctreeNode
    maxTrianglesPerNode = None # int
    maxDepth = None # int
    
    def __init__(self, root_position: list[float], root_scale: float, maxTrianglesPerNode: int = 10, maxDepth: int = 5):
        self.root = OctreeNode(root_position, root_scale)
        self.maxTrianglesPerNode = maxTrianglesPerNode
        self.maxDepth = maxDepth
    
    def InsertTriangles(self, node: OctreeNode, triangles: list[Triangle], depth: int):
        #Go through all triangles and remember them if they overlap with the region of this cube.
        containedTriangles = list()
        for triangle in triangles:
            #print(triangle.Vertices)
            if TriangleHelper.TriangleCubeOverlap(triangle, node.Position, node.Scale):
                containedTriangles.append(triangle)
        
        if len(containedTriangles) > self.maxTrianglesPerNode and depth < self.maxDepth:
            depth += 1
            node.Subdivide(depth)
            for child in node.Children:
                self.InsertTriangles(child, triangles, depth)
        else:
            node.Triangles.extend(containedTriangles)
    
    def Build(self, triangles: list[Triangle]):
        self.root.Subdivide(0)
        for child in self.root.Children:
            self.InsertTriangles(child, triangles, 0)

def Generate(root_position: list[float], root_scale: float, triangles: list[Triangle]):
    #print(root_position)
    octree = Octree(root_position, root_scale)
    octree.Build(triangles)
    return octree.root