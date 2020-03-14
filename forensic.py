def typeDetect(list4):
    type = "Unknown"
    if list4 == 0x06:
        type = "FAT-16"
    if list4 == 0x00:
        type = "NOT VALID"
    if list4 == 0x07:
        type = "NTFS"
    if list4 == 0x0B:
        type = "FAT-32"
    return type

#https://docs.microsoft.com/en-us/windows/win32/devnotes/attribute-list-entry
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
        bigEndian = bigEndian + "{:02x}".format(littleEndian[len(littleEndian)-1-x]) #reverse the input and store it in a string
    result = int(bigEndian, 16) #convert the string into an integer according to base 16
    return result

def analysePartitions(pos, num):
    print('Partition analysis')
    f.seek(pos) #offset our position in the disk according to pos
    partInfo = f.read(16) #stores the 64bits corresponding to the current partition in a list
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

def analyseFAT(bootTable):
    secPerCluster = bootTable[0x0D]
    bytePerSector = readBinary(bootTable[0x0B:0x0D])
    sizeReserve = bootTable[0x0D]
    print("The number of sectors per cluster is : ", secPerCluster)
    fatCopies = bootTable[0x10]
    sizeOneFAT = readBinary(bootTable[0x16:0x18])
    totalFATSize = fatCopies * sizeOneFAT
    print("The size of the FAT area is : ", totalFATSize, " sectors")
    rootDirEntrySize = 32 #Root directory entry is known to be 32 bytes
    noDirEntry = readBinary(bootTable[0x11:0x13])
    rootDirSize = int((rootDirEntrySize * noDirEntry)/bytePerSector)
    print("The size of the Root Directory is : ", rootDirSize  , " Sectors")
    startC2 = sizeReserve + rootDirSize + totalFATSize
    print("The start sector of cluster 2 is sector ", startC2, "\n")
    
def analyseNTFS(f):
    f.seek(512*1606500) #512 byte/sector * sector number + offset to get to BPB
    data = f.read(84) #store bytes from BPB
    bytePerSector = readBinary(data[0x0B:0x0D]) 
    print("Number of byte per sector is : ", bytePerSector)
    sectorPerCluster = data[0x0D]
    print("Number of sector per cluster is : ", sectorPerCluster)
    clusterMFT = readBinary(data[0x30:0x38])
    sectorMFT = clusterMFT * sectorPerCluster
    print("Sector address for the MFT file record is : ", sectorMFT)
    
    # Useful link https://www.writeblocked.org/resources/ntfs_cheat_sheets.pdf
    f.seek(512*(1606500+sectorMFT)) #Go to the start of the MFT record
    data = f.read(64) #Store the first 64 bytes - arbitrary values
    offsetAttribute = readBinary(data[0x14:0x16]) #read the informations in bytes 0x14 and 0x15 which is the offset to the first attribute
    f.seek(512*(1606500+sectorMFT)+offsetAttribute) #offset previous location
    data = f.read(10) #store data - arbitrary value
    type = readBinary(data[0:4]) #read the type store in the first 4 bytes
    length = readBinary(data[4:8]) #read the length of the attribute store in bytes 4-7
    print("1st attribute type is : ", attributeType(type), " length is : ", length)
    
    f.seek(512*(1606500+sectorMFT)+0x38+length) #goes to the next attribute by adding the length of previous attribute to current offset
    data = f.read(10) #store data, arbitrary value
    type = readBinary(data[0:4])
    length = readBinary(data[4:7])
    print("2nd attribute type is : ", attributeType(type), " length is : ", length)
    
    
    
    
with open("D:\\USBkey.dd", "rb") as f: #open Sample_1.dd
    
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
            list = [0x1BE, 0x1CE, 0x1DE, 0x1EE] #List containing the 4 places we have to offset to analyse the partitions
            while i < 4:
                partitionCount = partitionCount + analysePartitions(list[i], i+1)
                i = i + 1
                print("There are ", partitionCount, " valid partitions")
        elif num=='2':
            f.seek(0x7E00) # move to the beginning of partition 1
            bootTable = f.read(64) # store the 64 bytes of boot sector
            analyseFAT(bootTable)
        elif num=='3':
            analyseNTFS(f)
        elif num == '4':
            print('Exit')
        else:
            print("Please enter a valid Choice")    

    f.close() #closes Sample_1.dd


