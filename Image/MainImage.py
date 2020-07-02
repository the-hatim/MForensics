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
