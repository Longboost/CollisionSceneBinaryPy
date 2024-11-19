from struct import unpack_from

class BoundingBox:
    Min = None
    Max = None
    
    def Read(self, reader: bytearray, readOffset: int, byteOrder: str):
        self.Min = unpack_from(f'{byteOrder}3f', reader, offset=readOffset)
        readOffset += 12
        self.Max = unpack_from(f'{byteOrder}3f', reader, offset=readOffset)
    
    # def Write(self):
    
    def Compute(self, positions: list):
        minX = maxX = positions[0][0]
        minY = maxY = positions[0][1]
        minZ = maxZ = positions[0][2]
        
        for i in range(1,len(positions)):
            minX = min(minX, positions[i][0])
            minY = min(minY, positions[i][1])
            minZ = min(minZ, positions[i][2])
            maxX = max(maxX, positions[i][0])
            maxY = max(maxY, positions[i][1])
            maxZ = max(maxZ, positions[i][2])
        
        self.Min = (minX, minY, minZ)
        self.Max = (maxX, maxY, maxZ)