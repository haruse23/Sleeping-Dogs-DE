from inc_noesis import *
import os

# author: haru233
# Rename .perm.bin to ".sdde" and .temp.bin to ".sdde2"

def registerNoesisTypes():
    print("Registering Perm/Temp Texture plugin")
    handle = noesis.register("Perm/Temp Texture", ".sdde")
    noesis.setHandlerTypeCheck(handle, checkType)
    noesis.setHandlerLoadRGBA(handle, LoadTexture)

    noesis.setHandlerWriteRGBA(handle, WriteTexture)

    return 1

def checkType(data):
    return 1

def readCString(bs):
    chars = []
    while True:
        b = bs.readUByte()
        if b == 0:
            break
        chars.append(b)
    return bytes(chars).decode("ascii", errors="replace")

globalTextureData = []

def LoadTexture(data, texList):
    
    bs = NoeBitStream(data)

    ChunkID = bs.readUInt()
    ChunkSize = bs.readUInt()

    bs.seek(32, 1)
    TextureNameHash = bs.readUInt()
    bs.seek(20, 1)

    TextureMarker = bs.readUInt() # Always "BF FA 43 8B"
    TextureName = readCString(bs)

    bs.seek(40 - (len(TextureName) + 1), 1)
    
    print(bs.tell())
    TextureType = bs.readUInt()
    bs.seek(4, 1)

    Width = bs.readUShort()
    Height = bs.readUShort()

    bs.seek(16, 1)
    TextureSize = bs.readUInt()
    
    bs.seek(4, 1)
    TextureOffset = bs.readUInt() # Offset in .temp.bin file


    bs.seek(332, 1)

    FileSize = bs.getSize()
    TextureCount = FileSize // (ChunkSize + 16)

    

    # === Find the matching .temp.bin file ===
    permPath = rapi.getInputName()
    baseName = permPath.replace(".sdde", "")
    tempPath = baseName + ".sdde2"

    if not os.path.exists(tempPath):
        print("ERROR: Companion sdde2 file not found:", tempPath)
        return 0

    # === Load pixel data ===
    pixelData = rapi.loadIntoByteArray(tempPath)

    FileID = pixelData[:4]

    pixelData = pixelData[TextureOffset : TextureOffset + TextureSize]

    userData = {
            "ChunkID": ChunkID,
            "ChunkSize": ChunkSize,
            "TextureNameHash": TextureNameHash,
            "TextureMarker": TextureMarker,
            "TextureName": TextureName,
            "TextureType": TextureType,
            "Width": Width,
            "Height": Height,
            "TextureOffset": TextureOffset,
            "TextureSize": TextureSize,
            "FileID": FileID,
            "TextureCount": TextureCount,
            "PixelData": pixelData
        }
    
    

    if TextureType == 1:
        tex = NoeTexture(TextureName, Width, Height, pixelData, noesis.NOESISTEX_DXT1)
        texList.append(tex)
        globalTextureData.append(userData)

    elif TextureType == 3:
        tex = NoeTexture(TextureName, Width, Height, pixelData, noesis.NOESISTEX_DXT5)
        texList.append(tex)
        globalTextureData.append(userData)

    elif TextureType == 9:
        rgba = rapi.imageDecodeDXT(pixelData, Width, Height, noesis.FOURCC_BC5)
  

        # Build RGBA32 manually: R = X, G = Y, B = 0, A = 255
        px = bytearray(len(rgba))
        for i in range(Width * Height):
            px[i*4 + 0] = rgba[i*4 + 0]  # R
            px[i*4 + 1] = rgba[i*4 + 1]  # G
            px[i*4 + 2] = 0                  # B = 0
            px[i*4 + 3] = 255                # A = 255
                
        tex = NoeTexture(TextureName, Width, Height, px, noesis.NOESISTEX_RGBA32)
        texList.append(tex)
        globalTextureData.append(userData)

    else:
        print("Unsupported Texture Type: {}".format(TextureType))


    for i in range(TextureCount-1):
        ChunkID = bs.readUInt()
        ChunkSize = bs.readUInt()
        

        bs.seek(32, 1)
        TextureNameHash = bs.readUInt()
        bs.seek(20, 1)

        TextureMarker = bs.readUInt() # Always "BF FA 43 8B"
        TextureName = readCString(bs)

        bs.seek(40 - (len(TextureName) + 1), 1)
        
        print(bs.tell())
        TextureType = bs.readUInt()
        bs.seek(4, 1)

        Width = bs.readUShort()
        Height = bs.readUShort()
     
        bs.seek(16, 1)
        TextureSize = bs.readUInt()
        
        bs.seek(4, 1)
        TextureOffset = bs.readUInt()
     
        
        bs.seek(332, 1)

        
        # === Find the matching .temp.bin file ===
        permPath = rapi.getInputName()
        baseName = permPath.replace(".sdde", "")
        tempPath = baseName + ".sdde2"

        if not os.path.exists(tempPath):
            print("ERROR: Companion sd2 file not found:", tempPath)
            return 0

        # === Load pixel data ===
        pixelData = rapi.loadIntoByteArray(tempPath)

        FileID = pixelData[:4]

        pixelData = pixelData[TextureOffset : TextureOffset + TextureSize]

        userData = {
            "ChunkID": ChunkID,
            "ChunkSize": ChunkSize,
            "TextureNameHash": TextureNameHash,
            "TextureMarker": TextureMarker,
            "TextureName": TextureName,
            "TextureType": TextureType,
            "Width": Width,
            "Height": Height,
            "TextureOffset": TextureOffset,
            "TextureSize": TextureSize,
            "FileID": FileID,
            "TextureCount": TextureCount,
            "PixelData": pixelData
        }
       
        if TextureType == 1:
            tex = NoeTexture(TextureName, Width, Height, pixelData, noesis.NOESISTEX_DXT1)
            texList.append(tex)
            globalTextureData.append(userData)
    
        elif TextureType == 3:
            tex = NoeTexture(TextureName, Width, Height, pixelData, noesis.NOESISTEX_DXT5)
            texList.append(tex)
            globalTextureData.append(userData)

        elif TextureType == 9:
            rgba = rapi.imageDecodeDXT(pixelData, Width, Height, noesis.FOURCC_BC5)
            
            # Build RGBA32 manually: R = X, G = Y, B = 0, A = 255
            px = bytearray(len(rgba))
            for i in range(Width * Height):
                px[i*4 + 0] = rgba[i*4 + 0]  # R
                px[i*4 + 1] = rgba[i*4 + 1]  # G
                px[i*4 + 2] = 0                  # B = 0
                px[i*4 + 3] = 255                # A = 255
                
            tex = NoeTexture(TextureName, Width, Height, px, noesis.NOESISTEX_RGBA32)
            texList.append(tex)
            globalTextureData.append(userData)
            

        else:
            print("Unsupported Texture Type: {}".format(TextureType))



    InjectTexture(texList)

        

    return 1



def get_dds_format(dds_data):
    FOURCC_DXT1 = b'DXT1'
    FOURCC_DXT3 = b'DXT3'
    FOURCC_DXT5 = b'DXT5'
    
    if dds_data[84:88] == FOURCC_DXT1:
        return noesis.NOESISTEX_DXT1
    elif dds_data[84:88] == FOURCC_DXT3:
        return noesis.NOESISTEX_DXT3
    elif dds_data[84:88] == FOURCC_DXT5:
        return noesis.NOESISTEX_DXT5
    else:
        return None



def InjectTexture(texList):
    index_str = noesis.userPrompt(noesis.NOEUSERVAL_STRING, "Choose Index", "Enter the texture index to replace:", "0")
    if index_str is None:
        return
    
    index = int(index_str)

    dds_path = noesis.userPrompt(noesis.NOEUSERVAL_FILEPATH, "Select DDS", "Choose replacement DDS texture:", "")

    if not dds_path:
        return

    with open(dds_path, "rb") as f:
        new_data = f.read()

    new_tex = rapi.loadExternalTex(dds_path)
    texList[index] = new_tex

    new_pixel_data = new_data[128:]

    globalTextureData[index]["PixelData"] = new_pixel_data
    globalTextureData[index]["TextureSize"] = len(new_pixel_data)
    globalTextureData[index]["Width"] = new_tex.width
    globalTextureData[index]["Height"] = new_tex.height


    fmt = get_dds_format(new_data)
    if fmt == noesis.NOESISTEX_DXT1:
        globalTextureData[index]["TextureType"] = 1
    elif fmt == noesis.NOESISTEX_DXT3:
        globalTextureData[index]["TextureType"] = 2
    elif fmt == noesis.NOESISTEX_DXT5:
        globalTextureData[index]["TextureType"] = 3
    else:
        print("Warning: Injected texture format unsupported")

    offset = 16
    for tex in globalTextureData:
        tex["TextureOffset"] = offset
        offset = offset + tex["TextureSize"]

    print("Injected texture at index {} from: {}".format(index, dds_path))



def WriteTexture(data, Width, Height, bs):
    bs = NoeBitStream()
    ud = globalTextureData[0]
    TextureCount = ud.get("TextureCount")
    
    for i in range(TextureCount):
        ud = globalTextureData[i]

        ChunkID = ud.get("ChunkID")
        ChunkSize = ud.get("ChunkSize")
        TextureNameHash = ud.get("TextureNameHash")
        TextureMarker = ud.get("TextureMarker")
        TextureName = ud.get("TextureName")
        TextureType = ud.get("TextureType")
        Width = ud.get("Width")
        Height = ud.get("Height")
        TextureOffset = ud.get("TextureOffset")
        TextureSize = ud.get("TextureSize")

        bs.writeUInt(ChunkID)
        bs.writeUInt(ChunkSize)
        bs.writeUInt(ChunkSize)
        bs.writeBytes(b'\x00' * 16)


        bs.writeUInt(TextureNameHash)
        bs.writeBytes(b'\x00' * 8)
        bs.writeUInt(TextureMarker)
        bs.writeString(TextureName)
        bs.writeBytes(b'\x00' * (40 - (len(TextureName) + 1)))

        bs.writeUInt(TextureType)
        bs.writeBytes(b'\x00' * 4)

        bs.writeUShort(Width)
        bs.writeUShort(Height)
        bs.writeBytes(b'\x00' * 32)
        
        bs.writeUInt(TextureOffset)
        bs.writeUInt(TextureSize)
        bs.writeBytes(b'\x00' * 168)

    baseName = os.path.splitext(rapi.getOutputName())[0]
    dataFilePathSD = baseName + ".sdde"
    with open(dataFilePathSD, "wb") as f:
        f.write(bs.getBuffer())


    dataFilePathSD2 = baseName + ".sdde2"
    dataBS = NoeBitStream()

    FileID = ud.get("FileID")
    FileSize = 0

    for i in range(TextureCount):
        ud = globalTextureData[i]
        FileSize += ud.get("TextureSize")

    dataBS.writeBytes(FileID)
    dataBS.writeUInt(FileSize)
    dataBS.writeUInt(FileSize)
    dataBS.writeBytes(b'\x00' * 4)

    for i in range(TextureCount):
        ud = globalTextureData[i]
        pixelData = ud.get("PixelData")
        dataBS.writeBytes(pixelData)

    with open(dataFilePathSD2, "wb") as f:
        f.write(dataBS.getBuffer())
            


    return 1
