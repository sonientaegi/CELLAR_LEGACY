import os.path

from CELLAR             import authority
from CELLAR.index       import INDEX_FILE
from CELLAR.models      import UserInfo
from SonienStudio.file  import FileManager


class CELLAR_FileManager(FileManager):
    """
    CELLAR 에서 사용할 파일 메니져.
    FileManager 클래스를 상속받아 권한 확인 루틴 추가
    """
    def __init__(self, request):
        self.userinfo = UserInfo.getUserInfo(request)
        FileManager.__init__(self, self.userinfo.getUserHome())
     
    def getFileList(self, path) :
        """
        지정한 디렉토리의 하위 디렉토리와 파일 리스트를 이름순 대로 정렬하여 반환한다.
        return            : None 또는 ([디렉토리], [파일])
        디렉토리        : [ (basename, root 기준 상대 경로), ... ]
        파일            : [ (basename, root 기준 상대 경로, [확장자, 크기, root 기준 상대 경로]), ... ]
        """
        # 권한 관리 추가
        if authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x04) :
            fileList = super().getFileList(path)
            dirList = []
            for directory in fileList[0] :
                if self.isReadable(directory[1]) : 
                    dirList.append(directory)
              
            return (dirList, fileList[1])
        else :
            return None
     
    def getDirTree(self, path = "/", depth_to = 0, sortRule = lambda child : child[0]) :
        """ 
        지정한 경로로 부터 하위 디렉토리를 반환한다. 
        None 또는
        [ (basname, root 기준 상대경로, 하위[...]), ... ]
        """
        # 권한 관리 추가
         
        if authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x04) :
            return super().getDirTree(path, depth_to, sortRule)
        else :
            return None
         
    def isReadable(self, path):
        """
        사용자가 subPath 에 대한 읽기 권한이 있는지를 확인한다. 
        """
        return authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x04)
     
    def isWriteable(self, path):
        """
        사용자가 subPath 에 대한 쓰기 권한이 있는지를 확인한다. 
        """
        return authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x02)
     
    def isDeletable(self, path):
        """
        사용자가 subPath 에 대한 삭제 권한이 있는지를 확인한다. 
        """
        return authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x01)
     
    def getFullPath(self, subPath):
        return self.userinfo.getUserHome() + subPath
     
    def rename(self, src, dst):
        """
        0 : 성공
        1 : src 미존재
        2 : dst 미존재
        3 : 허용되지 않는 요청
        4 : 정체 불명
        5 : 권한 없음
        """
        if(not self.isWriteable(src)) :
            return 5
        else :
            return super().rename(src, dst) 
     
    def move(self, target, dst):
        """
        0 : 성공
        1 : target 미존재
        2 : dst 가 파일
        3 : 허용되지 않는 요청
        4 : 정체 불명
        5 : 권한 없음
        """
        if not self.isWriteable(dst) or not self.isDeletable(target) :
            return 5
        else :
            return super().move(target, dst);
     
    def mkdir(self, parentPath, dirName):
        """
        0 : 성공
        1 : 생성 위치가 존재하지 않습니다
        2 : 생성 위치가 파일입니다
        3 : 허용되지 않는 요청입니다
        4 : 오류가 발생하였습니다
        5 : 권한 없음
        """
        if not self.isWriteable(parentPath) :
            return 5
        else :
            return super().mkdir(parentPath, dirName)
         
    def rmdir(self, dirPath):
        """
        0 : 성공
        1 : 대상이 파일입니다
        2 : -
        3 : 허용되지 않은 요청입니다
        4 : 오류가 발생하였습니다
        5 : 권한 없음
        """
        if not self.isDeletable(dirPath) :
            return 5
        else :
            return super().rmdir(dirPath)
     
    def rmfile(self, filePath): 
        """
        0 : 성공
        1 : 대상이 경로입니다
        2 : -
        3 : 허용되지 않은 요청입니다
        4 : 오류가 발생하였습니다
        5 : 권한 없음
        """
        dirPath = os.path.normpath(os.path.dirname(filePath))
        if not self.isDeletable(dirPath) :
            return 5
        else :
            return super().rmfile(dirPath)
         
    def rmfiles(self, targetPath, filenames):
        """
        return [(filename, errno), ...]
         
        0 : 성공
        1 : 대상이 경로입니다
        2 : -
        3 : 허용되지 않은 요청입니다
        4 : 오류가 발생하였습니다
        5 : 권한 없음
        """
        result  = []
        dirAuth = self.isDeletable(targetPath)  
        for filename in filenames :
            filePath = targetPath + filename
            code = 0
            if not dirAuth or not self.isDeletable(filePath) :
                code = 5
            else :
                code = super().rmfile(filePath)  
         
            result.append((filename, code))
                           
        return result
 
def getFileGroup(request, path):
    manager = CELLAR_FileManager(request)
    files = manager.getFileList(path)
     
    if files is None :
        return ([],[])
     
    # 디렉토리 ID 식별자는 조회 대상에서 제외
    descriptor = None
    for file in files[1] :
        if file[0] == INDEX_FILE :
            descriptor = file
            break
         
    if descriptor != None :
        files[1].remove(descriptor)
     
    return manager.groupFileList(files)
 
def getDirTree(request, path, depth_to = 1):
    manager = CELLAR_FileManager(request)
    dirTree = manager.getDirTree(path, depth_to)
     
    if dirTree is None :
        return []
     
    return dirTree