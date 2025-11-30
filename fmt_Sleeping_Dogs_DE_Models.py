# author: haru233

from inc_noesis import *
import struct

def registerNoesisTypes():
    handle = noesis.register("Sleeping Dogs Definitive Edition Model", ".binDE")
    noesis.setHandlerTypeCheck(handle, checkType)
    noesis.setHandlerLoadModel(handle, LoadModel)
    return 1

def checkType(data):
    return 1

def LoadModel(data, mdlList):
    bs = NoeBitStream(data)

    
    ModelCount = 0
    IndexBuffers = {}
    VertexBuffers_1 = {} # Mainly Positions Buffer
    VertexBuffers_2 = {} # Mainly Weights Buffer
    VertexBuffers_3 = {} # Mainly UV Buffer
    ModelTableOffsets = []

    while bs.tell() < len(data):
        print("Starting LoadModel...")

        

        ChunkID = bs.readUInt()
        bs.seek(4, 1)
        ChunkSize = bs.readUInt()
        PaddingSize = bs.readUInt()

        curOffset = bs.tell()
        print("At offset " + str(curOffset) + ", ChunkID: " + str(ChunkID) + ", ChunkSize: " + str(ChunkSize))
        
        bs.seek(PaddingSize, 1)

        if ChunkID == 2056721529:
            # Save buffer ID and current stream position
            bs.seek(24, 1)
            bufferIDPos = bs.tell()
            BufferID = bs.readUInt()
            bs.seek(24, 1)
            BufferNameBytes = bs.readBytes(36)
            BufferName = BufferNameBytes.decode('utf-8', errors='ignore').rstrip('\x00')    
            bs.seek(16, 1)
            Stride = bs.readUInt()

            
            if "Index" in BufferName:
                IndexBuffers[BufferID] = {"IndexBufferIDOffset": bufferIDPos, "Stride": Stride}
                print("Added IndexBuffer ID " + str(BufferID) + " at pos " + str(bufferIDPos))

            elif "0.0" in BufferName:
                VertexBuffers_1[BufferID] = bufferIDPos
                print("Added VertexBuffer_1 ID " + str(BufferID) + " at pos " + str(bufferIDPos))
                
            elif "1.0" in BufferName:
                VertexBuffers_2[BufferID] = bufferIDPos
                print("Added VertexBuffer_2 ID " + str(BufferID) + " at pos " + str(bufferIDPos))

            elif "2.0" in BufferName:
                VertexBuffers_3[BufferID] = bufferIDPos
                print("Added VertexBuffer_3 ID " + str(BufferID) + " at pos " + str(bufferIDPos))

            bs.seek(curOffset + ChunkSize, 0)

            continue

        elif ChunkID == 1845060531:
            ModelCount += 1
            ModelTableOffsets.append(curOffset)
            bs.seek(curOffset + ChunkSize, 0)
            print("Found ModelTable chunk at offset " + str(curOffset) + " (ModelCount=" + str(ModelCount) + ")")

            continue
            
            
        elif ChunkID == 2552518363:
            # Save buffer ID and current stream position
            bs.seek(24, 1)
            bufferIDPos = bs.tell()
            BufferID = bs.readUInt()
            bs.seek(24, 1)
            BufferNameBytes = bs.readBytes(36)
            BufferName = BufferNameBytes.decode('utf-8', errors='ignore').rstrip('\x00')    
            bs.seek(4, 1)
            BoneCount = bs.readUInt()
            
            print("Found Bone Palette at Offset {}, BoneCount is {}".format(curOffset, BoneCount))
            bs.seek(curOffset + ChunkSize, 0)
            
            

        elif ChunkID == 3925339657:
            bs.seek(curOffset + ChunkSize, 0)
            
            if bs.tell() < len(data):
                Read1 = bs.readUInt()
                Read2 = bs.readUInt()
                Read3 = bs.readUInt()
                Read4 = bs.readUInt()

                if Read2 + Read4 == Read3:
                    bs.seek(Read2, 1)
                    continue
                
                else:
                    bs.seek(-16, 1)
                    continue

            else:
                continue

        else:
            bs.seek(curOffset + ChunkSize, 0)

    print("IndexBuffers found: " + str(len(IndexBuffers)) + ", VertexBuffers_1 found: " + str(len(VertexBuffers_1)) + ", VertexBuffers_3 found: " + str(len(VertexBuffers_3)))
    print("Model tables found: " + str(len(ModelTableOffsets)))

        


    for ModelIndex, ModelTableOffset in enumerate(ModelTableOffsets):
        print("Processing model " + str(ModelIndex) + " at offset " + str(ModelTableOffset))

        meshList = []

        print(ModelTableOffset)
        bs.seek(ModelTableOffset, 0)
        print(bs.tell())
        
        bs.seek(52, 1)
        bs.seek(36, 1)
        bs.seek(96, 1)

        Read = bs.readBytes(152)
        print(bs.tell())
        MeshPrimitiveCount = Read[8]
        print("MeshPrimitiveCount: " + str(MeshPrimitiveCount))
        
        
        FinalBlockSize = bs.readUInt() # (Final Block is basically 16 bytes -- first 4 bytes of them is the FinalBlockSize -- + MeshPrimitiveOFfsetsList + MeshTable)
        # MeshTable Size = FinalBlockSize - 16 - MeshPrimitiveOffsetsList Size (which is MeshPrimitiveCount * 8)
        
        bs.seek(12, 1)
        
        MeshPrimitiveOffsetsListStart = bs.tell()
        print(MeshPrimitiveOffsetsListStart)
        
        
        CurrentMeshPrimitiveOffsetPositionList = []
        
        
        MeshPrimitiveOffsetsList = []
        
        
        MeshPrimitiveOffsetsListSize = MeshPrimitiveCount * 8
        for i in range(MeshPrimitiveCount):
            CurrentMeshPrimitiveOffsetPosition = bs.tell()
            
            MeshPrimitiveOffset = bs.readUInt64() # Each offset is Relative to the current position of the cursor where it starts reading MeshPrimitiveOffset
            MeshPrimitiveOffsetsList.append(MeshPrimitiveOffset)
            
            CurrentMeshPrimitiveOffsetPositionList.append(CurrentMeshPrimitiveOffsetPosition)
            
            print(MeshPrimitiveOffset)
        
    
        MeshPrimitiveInfoList = []

        print("IndexBuffers:", IndexBuffers)
        print("VertexBuffers_1:", VertexBuffers_1)

        IndexBufferIDList = []
        VertexBuffer1_IDList = []

        VertexBuffer3_IDList = []   

        

        
        for i in range(MeshPrimitiveCount):
            
            
            bs.seek(CurrentMeshPrimitiveOffsetPositionList[i] + MeshPrimitiveOffsetsList[i], 0)
      
            bs.seek(24, 1)
            MaterialBufferID = bs.readUInt()
            
            bs.seek(28, 1)
            
            VertexDeclarationID = bs.readUInt()
            
            bs.seek(28, 1)
            
            IndexBufferID = bs.readUInt()
            IndexBufferIDList.append(IndexBufferID)
            print(bs.tell())
            
            bs.seek(28, 1)
            VertexBuffer1_ID = bs.readUInt()
            VertexBuffer1_IDList.append(VertexBuffer1_ID)
            
            bs.seek(28, 1)
            VertexBuffer2_ID = bs.readUInt()
            
            bs.seek(28, 1)
            VertexBuffer3_ID = bs.readUInt()
            
            print(bs.tell())
            
            bs.seek(40, 1)
            
            
            MeshPrimitiveOffsetInIndexBuffer = bs.readUInt()
            
                
            TriangleCount = bs.readUInt()
            
            print("MeshPrimitive {}: IndexBufferID={}, VertexBufferID={}, Offset={}, Triangles={}".format(
                i, IndexBufferID, VertexBuffer1_ID, MeshPrimitiveOffsetInIndexBuffer, TriangleCount))
            
            MeshPrimitiveInfoList.append({
                "MaterialBufferID": MaterialBufferID,
                "VertexDeclarationID": VertexDeclarationID,
                "IndexBufferID": IndexBufferID,
                "VertexBuffer1_ID": VertexBuffer1_ID,
                "VertexBuffer2_ID": VertexBuffer2_ID,
                "VertexBuffer3_ID": VertexBuffer3_ID,
                "IndexOffset": MeshPrimitiveOffsetInIndexBuffer,
                "TriangleCount": TriangleCount
            })
            
            
            
        
        
        for i, MeshPrim in enumerate(MeshPrimitiveInfoList):

            Indices = []
            Positions = []
            Normals = []
            Tangents = []
            UVs0 = []
            UVs1 = []
            Colors0 = []
            BlendIndicesAndWeights = []

            vertexDeclarationID = MeshPrim["VertexDeclarationID"]
            indexBufferID = MeshPrim["IndexBufferID"]
            vertexBuffer1_ID = MeshPrim["VertexBuffer1_ID"]
            vertexBuffer2_ID = MeshPrim["VertexBuffer2_ID"]
            vertexBuffer3_ID = MeshPrim["VertexBuffer3_ID"]
            indexOffset = MeshPrim["IndexOffset"]
            triangleCount = MeshPrim["TriangleCount"]

            print(indexBufferID)
            print(vertexBuffer1_ID)
            print(indexOffset)
            print(triangleCount)

            # === Index buffer ===
            if indexBufferID not in IndexBuffers:
                print("Skipping this Mesh Primitive, it doesn't have Index Buffer Reference")
                print(indexBufferID)
                continue


            if indexBufferID in IndexBuffers:
                
                IndexInfo = IndexBuffers[indexBufferID]
                
                if IndexInfo["Stride"] == 2:
                    bs.seek(IndexInfo["IndexBufferIDOffset"] + 280 + indexOffset * 2, 0) 
                    
                
                elif IndexInfo["Stride"] == 4:
                    bs.seek(IndexInfo["IndexBufferIDOffset"] + 280 + indexOffset * 4, 0)
                    

                
                print(" --> Mesh {}: Reading {} indices from offset {}".format(i, triangleCount * 3, IndexInfo["IndexBufferIDOffset"] + 280 + indexOffset * 2))
                print(" --> First 6 indices: {}".format(Indices[:6]))
                
                for t in range(triangleCount * 3):
                  if IndexInfo["Stride"] == 2:
                    Indices.append(bs.readUShort())
                  
                  elif IndexInfo["Stride"] == 4:
                    Indices.append(bs.readUInt())

             
            # === Vertex Buffers ===
            if vertexBuffer1_ID in VertexBuffers_1:
                bs.seek(VertexBuffers_1[vertexBuffer1_ID], 0)
                bs.seek(80, 1)
                VertexStride = bs.readUInt()
                VertexCount = bs.readUInt()
                bs.seek(192, 1)

                for j in range(VertexCount):
                    if vertexDeclarationID == 661362023:
                        p1 = bs.readFloat()
                        p2 = bs.readFloat()
                        p3 = bs.readFloat() 
                        p4 = bs.readFloat() 

                        n1 = bs.readUByte() / 255.0
                        n2 = bs.readUByte() / 255.0
                        n3 = bs.readUByte() / 255.0
                        n4 = bs.readUByte() / 255.0

                        t1 = bs.readUByte() / 255.0
                        t2 = bs.readUByte() / 255.0
                        t3 = bs.readUByte() / 255.0
                        t4 = bs.readUByte() / 255.0

                        Positions.append(NoeVec3([p1, p2, p3]))
                        Normals.append(NoeVec3([n1, n2, n3]))
                        Tangents.append(NoeVec4([t1, t2, t3, t4]))

                    elif vertexDeclarationID == 2434669137 or vertexDeclarationID == 4067430294:
                        p1 = bs.readFloat()
                        p2 = bs.readFloat()
                        p3 = bs.readFloat()

                     
                        Positions.append(NoeVec3([p1, p2, p3]))
 
            
            if vertexBuffer2_ID in VertexBuffers_2:
                bs.seek(VertexBuffers_2[vertexBuffer2_ID], 0)
                bs.seek(80, 1)
                VertexStride = bs.readUInt()
                VertexCount = bs.readUInt()
                bs.seek(192, 1)
                print(bs.tell())

                for j in range(VertexCount):                
                    if vertexDeclarationID == 661362023:
                        BlendIndex1 = bs.readUByte()
                        BlendIndex2 = bs.readUByte()
                        BlendIndex3 = bs.readUByte()
                        BlendIndex4 = bs.readUByte()
                        
                        BlendWeight1 = bs.readUByte() / 255.0
                        BlendWeight2 = bs.readUByte() / 255.0
                        BlendWeight3 = bs.readUByte() / 255.0
                        BlendWeight4 = bs.readUByte() / 255.0
                        
                        
                        BlendIndicesAndWeights.append(NoeVertWeight([BlendIndex1, BlendIndex2, BlendIndex3, BlendIndex4], [BlendWeight1, BlendWeight2, BlendWeight3, BlendWeight4]))
                        
                    
                    elif vertexDeclarationID == 2434669137:
                        U = bs.readHalfFloat()
                        V = bs.readHalfFloat()
                        
                        n1 = bs.readByte() / 127.0
                        n2 = bs.readByte() / 127.0
                        n3 = bs.readByte() / 127.0
                        n4 = bs.readByte() / 127.0
                        
                        t1 = bs.readByte() / 127.0
                        t2 = bs.readByte() / 127.0
                        t3 = bs.readByte() / 127.0
                        t4 = bs.readByte() / 127.0
                        
                        R = bs.readUByte() / 255.0
                        G = bs.readUByte() / 255.0
                        B = bs.readUByte() / 255.0
                        A = bs.readUByte() / 255.0
                        
                        UVs0.append(NoeVec3([U, V, 0.0]))
                        Normals.append(NoeVec4([n1, n2, n3]))
                        Tangents.append(NoeVec4([t1, t2, t3, t4]))
                        Colors0.append(NoeVec4([R, G, B, A]))
                        
                    
                    
                    elif vertexDeclarationID == 4067430294:
                        U = bs.readHalfFloat()
                        V = bs.readHalfFloat()
                        
                        n1 = bs.readByte() / 127.0
                        n2 = bs.readByte() / 127.0
                        n3 = bs.readByte() / 127.0
                        n4 = bs.readByte() / 127.0
                        
                        UVs0.append(NoeVec3([U, V, 0.0]))
                        Normals.append(NoeVec4([n1, n2, n3]))
                        
                        
                        
                        

                        

            if vertexBuffer3_ID in VertexBuffers_3:
                bs.seek(VertexBuffers_3[vertexBuffer3_ID], 0)
                bs.seek(80, 1)
                VertexStride = bs.readUInt()
                VertexCount = bs.readUInt()
                bs.seek(192, 1)
                print(bs.tell())

                for j in range(VertexCount):
                    if vertexDeclarationID == 661362023:
                        U = bs.readHalfFloat()
                        V = bs.readHalfFloat()
                        
   
                        
                        UVs0.append(NoeVec3([U, V, 0.0]))

            # === Build mesh ===
           

            mesh = NoeMesh(Indices, Positions, "mesh_{}_{}".format(ModelIndex, i))
            mesh.setNormals(Normals)
            mesh.setUVs(UVs0)
            mesh.setColors(Colors0)
            mesh.setWeights(BlendIndicesAndWeights)
       
            meshList.append(mesh)

            
        if meshList:
            Bones = []

            for i in range(BoneCount):
                m = NoeMat43()  # identity matrix
                
                Bone = NoeBone(i, "Bone_" + str(i), m, None, 0)
                Bones.append(Bone)
            
            if Bones:
                mdl = NoeModel(meshList, Bones)
                
            mdlList.append(mdl)
        else:
            print("⚠ No valid meshes found; skipping model append.")


        
        
        print("LoadModel finished successfully.")



    return 1

    
