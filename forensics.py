def typeDetect(list4):
    type = "Unknown"
    if list4 == 0x01:
        type = "FAT-12"
    if list4 == 0x05:
        type = "Extended MS-DOS Partition"
    if list4 == 0x06 or list4 == 0x04 or list4 == 0x0E:
        type = "FAT-16"
    if list4 == 0x00:
        type = "NOT VALID"
    if list4 == 0x07:
        type = "NTFS"
    if list4 == 0x0B or list4 == 0x0C:
        type = "FAT-32"
    return type


def attributeType(value):
    type = ''
    if value == 0x10:
        type = '$STANDARD_INFORMATION'
    if value == 0x20:
        type = 'ATTRIBUTE_LIST'
    if value == 0x30:
        type = '$FILE_NAME'
    if value == 0x40:
        type = '$OBJECT_ID'
    if value == 0x60:
        type = '$VOLUME_NAME'
    if value == 0x70:
        type = '$VOLUME_INFORMATION'
    if value == 0x80:
        type = '$DATA'
    if value == 0x90:
        type = '$INDEX_ROOT'
    if value == 0xA0:
        type = '$INDEX_ALLOCATION'
    if value == 0xB0:
        type = '0xB0'
    if value == 0xC0:
        type = '0xC0'
    return type

def readBinary(littleEndian):
    bigEndian = "0x"
    for x in range(0, len(littleEndian)):
        bigEndian = bigEndian + "{:02x}".format(littleEndian[len(littleEndian)-1-x]) 
    result = int(bigEndian, 16) 
    return result

def analysePartitions(pos, num):
    print('Partition analysis')
    f.seek(pos) 
    partInfo = f.read(16) 
    print("Partition: ", num)
    type = typeDetect(partInfo[4])
    print("Type : ", type)
    print("Size : ", readBinary(partInfo[12:16]))
    print("Start :", readBinary(partInfo[8:12]))
    print("\n")
    if type != "NOT VALID":
        return 1
    else:
        return 0

def analyseFAT16(bootTable):
    print("FAT-16 Partition\n")
    secPerCluster = bootTable[0x0D]
    bytePerSector = readBinary(bootTable[0x0B:0x0D])
    sizeReserve = bootTable[0x0E]
    print("The number of sectors per cluster is : ", secPerCluster)
    fatCopies = bootTable[0x10]
    sizeOneFAT = readBinary(bootTable[0x16:0x18])
    totalFATSize = fatCopies * sizeOneFAT
    print("The size of the FAT area is : ", totalFATSize, " sectors")
    rootDirEntrySize = 32 
    noDirEntry = readBinary(bootTable[0x11:0x13])
    rootDirSize = int((rootDirEntrySize * noDirEntry)/bytePerSector)
    print("The size of the Root Directory is : ", rootDirSize  , " Sectors")
    startC2 = sizeReserve + rootDirSize + totalFATSize
    print("The start sector of cluster 2 is sector ", startC2, "\n")
    
def analyseFAT32(bootTable):
    print("FAT-32 Partition\n")
    secPerCluster = bootTable[0x0D]
    bytePerSector = readBinary(bootTable[0x0B:0x0D])
    sizeReserve = bootTable[0x0E]
    print("The number of sectors per cluster is : ", secPerCluster)
    fatCopies = bootTable[0x10]
    sizeOneFAT = readBinary(bootTable[0x24:0x28])
    totalFATSize = fatCopies * sizeOneFAT
    print("The size of the FAT area is : ", totalFATSize, " sectors")
    rootDirEntrySize = 32 
    noDirEntry = readBinary(bootTable[0x11:0x13])
    rootDirSize = int((rootDirEntrySize * noDirEntry)/bytePerSector)
    startC2 = sizeReserve + rootDirSize + totalFATSize
    print("The start sector of cluster 2 is sector ", startC2, "\n")
    
def analyseNTFS(f):
    i = 0
    list = [0x1BE, 0x1CE, 0x1DE, 0x1EE]
    while i < 4:
        f.seek(list[i])
        partInfo = f.read(16)
        if typeDetect(partInfo[4]) == "NTFS":
            start = readBinary(partInfo[8:12])
        i+=1
   
    f.seek(512*start) 
    data = f.read(84)
    bytePerSector = readBinary(data[0x0B:0x0D]) 
    print("Number of byte per sector is : ", bytePerSector)
    sectorPerCluster = data[0x0D]
    print("Number of sector per cluster is : ", sectorPerCluster)
    clusterMFT = readBinary(data[0x30:0x38]) 
    sectorMFT = clusterMFT * sectorPerCluster
    print("Sector address for the MFT file record is : ", sectorMFT)
    
   
    f.seek(512*(start+sectorMFT)) 
    data = f.read(64) 
    offsetAttribute = readBinary(data[0x14:0x16]) 
    f.seek(512*(start+sectorMFT)+offsetAttribute) 
    data = f.read(10) 
    type = readBinary(data[0:4]) 
    length = readBinary(data[4:8]) 
    print("1st attribute type is : ", attributeType(type), " length is : ", length)
    
    f.seek(512*(start+sectorMFT)+0x38+length) 
    data = f.read(10)
    type = readBinary(data[0:4])
    length = readBinary(data[4:8])
    print("2nd attribute type is : ", attributeType(type), " length is : ", length, "\n")
    
    
    
    
with open("D:\\demo", "rb") as f: #Edit this line;place the file or disk image you want to analyze
    
    num = ''
    while num != '4':
        print ("-------------------ENTER YOUR CHOICE------------------")    
        print (     "1.Partition Information")
        print (     "2.FAT Volume Information")
        print (     "3.NTFS Volume Information")
        print (     "4.Exit")
        print ("  -----------------------------------------------------")
    
    
        num=input('Choice :')
        
        if num=='1':
            i = 0
            partitionCount = 0 
            list = [0x1BE, 0x1CE, 0x1DE, 0x1EE] 
            while i < 4:
                partitionCount = partitionCount + analysePartitions(list[i], i+1)
                i = i + 1
            print("There are ", partitionCount, " valid partitions")
        elif num=='2':
            i = 0
            while i < 4:
                f.seek(list[i])
                partInfo = f.read(16)
                if typeDetect(partInfo[4]) == "FAT-16":
                    start = readBinary(partInfo[8:12])
                    f.seek(start*512)
                    bootTable = f.read(64) 
                    analyseFAT16(bootTable)
                if typeDetect(partInfo[4]) == "FAT-32":
                    start = readBinary(partInfo[8:12])
                    f.seek(start*512) 
                    bootTable = f.read(64) 
                    analyseFAT32(bootTable)
                i+=1
        elif num=='3':
            analyseNTFS(f)
        elif num == '4':
            print('Exit')
        else:
            print("Please enter a valid Choice")    

    f.close() 


