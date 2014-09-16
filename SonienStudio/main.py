from SonienStudio.tarstream     import TarStream
from datetime import datetime

TarStream.setSystemEncidiong("euc-kr")
tarStream = TarStream.open(r"C:\Program Files\SonienStudio\Workspaces\Python3\TarStream")
tarStream.add(r"에이.jpg")
tarStream.add(r"비이.jpg")
tarStream.add(r"씨.jpg")  

now = datetime.now()
tarFile = open("{0:02d}{1:02d}{2:02d}.tar".format(now.hour, now.minute, now.second), mode='bw')
for block in tarStream :
    print(block.__len__())
    tarFile.write(block)
    
tarFile.close()

