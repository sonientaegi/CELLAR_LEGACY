import os.path

from CELLAR             import authority, config
from CELLAR.models      import UserInfo
from SonienStudio.file  import FileManager


class CELLAR_FileManager(FileManager):
    """
    FileManager implemented class for CELLAR
    Add checking authority for each transactions.
    
    Every "path" means relative path from Home-Path of the requesting user.
    Every "path" parameters should be ended with "/"
    """
    def __init__(self, request):
        self.userinfo = UserInfo.getUserInfo(request)
        FileManager.__init__(self, self.userinfo.getHomePath())
     
    def getFileList(self, path) :
        """
        Returns two groups of directories and files of the [path] sorted by name.
        Remove CELLAR index file from the list.
        
        @return: 
            None if user doesn't have reading authority
            
            - or -
            
            (
                Directory [
                    Directory1 (
                        basename,
                        path,
                    ),
                    Directory2,
                    Directory3,
                    ...
                ],
                
                File [
                    File1 (
                        basename,
                        path,
                        size
                    ),
                    File2,
                    File3,
                    ...
                ]
            )
                                
        """
        
        if authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x04) :
            fileList = super().getFileList(path)
            
            files = []
            for file in fileList[1] :
                if file[0] == config.INDEX_FILE :
                    continue
                else :
                    files.append(file)
            
            dirs = []
            for directory in fileList[0] :
                if self.isReadable(directory[1]) : 
                    dirs.append(directory)
              
            return (dirs, files)
        else :
            return None
     
    def getDirTree(self, path = "/", depth_to = 0, sortRule = lambda child : child[0]) :
        """ 
        Returns tree of sub-directories
        
        @return:
            None if user doesn't have reading authority
            
            - or - 
            
            [
                Directory1 (
                    basename,
                    path,
                    sub-directory [
                        Directory1A(
                            basename,
                            path,
                            sub-directory [
                                Direcotry1Aa,
                                Directory1Ab,
                                Directory1Ac,
                                ...
                            ]
                        ),
                        Directory1B,
                        Directory1C,
                        ...
                    ]
                ),
                Directory2,
                Direcotyr3,
                ...
            ]
        """
        
        if authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x04) :
            return super().getDirTree(path, depth_to, sortRule)
        else :
            return None
         
    def isReadable(self, path):
        """
        Return whether the user has reading authority. 
        @return: Boolean
        """
        return authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x04)
     
    def isWriteable(self, path):
        """
        Return whether the user has writing authority. 
        @return: Boolean
        """
        return authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x02)
     
    def isDeletable(self, path):
        """
        Return whether the user has deleting authority. 
        @return: Boolean
        """
        return authority.Directory.isAuthorized(self.userinfo, self.getFullPath(path), 0x01)
     
    def getFullPath(self, subPath):
        """
        Return full path of subPath. Simply concatenate user's Home Path and subPath
        
        """
        return self.userinfo.getHomePath() + subPath
     
    def rename(self, src, dst):
        """
        Renames directory or file.
        
        @return: 
            0 : Success
            1 : src doesn't exist
            2 : dst doesn't exist
            3 : Illeagal request
            4 : Unknown error
            5 : User doesn't have writing authority
        """
        if(not self.isWriteable(src)) :
            return 5
        else :
            return super().rename(src, dst) 
     
    def move(self, target, dst):
        """
        Moves target to dst. target can be a file or directory. But dst should be a directory.
        User must have writing authority of dst and deleting authority of target.
        
        @return: 
            0 : Success
            1 : target doesn't exist
            2 : dst is file
            3 : Illegal request
            4 : Unknown error
            5 : User doesn't have writing and deleting authority
        """
        if not self.isWriteable(dst) or not self.isDeletable(target) :
            return 5
        else :
            return super().move(target, dst);
     
    def mkdir(self, parentPath, dirName):
        """
        Make a new directory
        
        @return:
            0 : Success
            1 : parentPath doesn't exist
            2 : parentPath is file
            3 : Illegal request
            4 : Unknown error
            5 : User doesn't have writing authority
        """
        if not self.isWriteable(parentPath) :
            return 5
        else :
            return super().mkdir(parentPath, dirName)
         
    def rmdir(self, dirPath):
        """
        Delete a directory
        
        @return:
            0 : Success
            1 : dirPath is file
            2 : -
            3 : Illegal request
            4 : Unknown error
            5 : User doesn't have deleting authority
        """
        if not self.isDeletable(dirPath) :
            return 5
        else :
            return super().rmdir(dirPath)
     
    def rmfile(self, filePath): 
        """
        Delete a file
        
        @return:
            0 : Success
            1 : filePath is not a file
            2 : -
            3 : Illegal request
            4 : Unknown error
            5 : User doesn't have deleting authority
        """
        dirPath = os.path.normpath(os.path.dirname(filePath))
        if not self.isDeletable(dirPath) :
            return 5
        else :
            return super().rmfile(dirPath)
         
    def rmfiles(self, targetPath, filenames):
        """
        Delete a bunch of files.
        @param targetPath: common path of files.
        @param filenames: Array of names of file
        
        @return:
            [ 
                target1 ( 
                    filename,
                    error code
                ),
                target2,
                target3,
                ...
            ]
        
            error code :
                0 : Success
                1 : target is directory
                2 : -
                3 : Illegal request
                4 : Unknown error
                5 : User doesn't have deleting authority
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
    """
    Short function for CELLAR_
    """
    fileGroup = CELLAR_FileManager(request).getFileGroup(path)
    if fileGroup is None :
        fileGroup = []
    
    return fileGroup
 
def getDirTree(request, path, depth_to = 1):
    dirTree = CELLAR_FileManager(request).getDirTree(path, depth_to)
     
    if dirTree is None :
        dirTree = []
     
    return dirTree