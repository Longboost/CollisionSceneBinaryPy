from Triangle import *
import numpy as np

#Based on this algorithm: http:#jgt.akpeters.com/papers/AkenineMoller01/tribox.html

# ---- METHODS (PUBLIC) --------------------------------------------------------------------------------------

## <summary>
## Returns a value indicating whether the given <paramref name="triangle"/> overlaps a cube positioned at the
## <paramref name="cubeCenter"/> expanding with <paramref name="cubeHalfSize"/>.
## </summary>
## <param name="triangle">The <see cref="Triangle"/> to check for overlaps.</param>
## <param name="cubeCenter">The positional <see cref="Vector3F "/> at which the cube originates.</param>
## <param name="cubeHalfSize">The half length of one edge of the cube.</param>
## <returns><c>true</c> when the triangle intersects with the cube, otherwise <c>false</c>.</returns>
def TriangleCubeOverlap(t: Triangle, Position: list[float], BoxSize: float) -> bool:
    triangle = t
    boxCenter = np.array(Position)
    boxHalfSize = BoxSize

    #Ignore height for now
    #Octrees just divide by width/depth
    box_height = 10000.0

    # Get the AABB bounds
    boxMin = boxCenter - np.array([boxHalfSize, box_height, boxHalfSize]);
    boxMax = boxCenter + np.array([boxHalfSize, box_height, boxHalfSize]);

    # Test each axis of the box
    if (min(triangle.Vertices[0][0], min(triangle.Vertices[1][0], triangle.Vertices[2][0])) > boxMax[0]): return False
    if (max(triangle.Vertices[0][0], max(triangle.Vertices[1][0], triangle.Vertices[2][0])) < boxMin[0]): return False
    if (min(triangle.Vertices[0][1], min(triangle.Vertices[1][1], triangle.Vertices[2][1])) > boxMax[1]): return False
    if (max(triangle.Vertices[0][1], max(triangle.Vertices[1][1], triangle.Vertices[2][1])) < boxMin[1]): return False
    if (min(triangle.Vertices[0][2], min(triangle.Vertices[1][2], triangle.Vertices[2][2])) > boxMax[2]): return False
    if (max(triangle.Vertices[0][2], max(triangle.Vertices[1][2], triangle.Vertices[2][2])) < boxMin[2]): return False

    # More accurate tests can be added here for edge cases

    return True;