import os.path
import math
from tempfile import TemporaryFile


class TarStream :
    BLOCK_SIZE  = 512
    SPACE       = 0x20
    ZERO        = 0x30
    NULL        = 0x00
    
    _encoding = "UTF-8"  
    
    def __init__(self, cwd, blocks = 1):
        self._filelist  = []
        self._cwd       = cwd
        self._size      = TarStream.BLOCK_SIZE * 2
        self._blocks    = blocks
        self._EOS       = True

    @staticmethod
    def arrayCopy(source, target, target_offset = 0):
        offset = target_offset
        for c in source :
            target[offset] = c 
            offset = offset + 1
            
    @staticmethod
    def arrayFill(target, value, offset, length):
        for i in range(offset, offset + length) :
            target[i] = value 
            
    @classmethod
    def setSystemEncidiong(cls, encoding):
        cls._encoding = encoding
    
    @staticmethod
    def open(cwd, blocks = 1):
        if cwd[-1] == os.path.sep :
            cwd = cwd[0:-1]
        return TarStream(cwd, blocks)
    
    def add(self, filename, subDir = None):
        fullPath = self._cwd
        if subDir != None and subDir[1] == os.path.sep :
            subDir = subDir[1:subDir.__len__()]
            fullPath = os.path.join(fullPath, subDir)
        fullPath = os.path.join(fullPath, filename)
        
        # 1. Create TAR header
        file = open(fullPath, mode='br')
        stat = os.stat(fullPath)
        header = bytearray(TarStream.BLOCK_SIZE)
                           
        # 1-1. 이름
        # 000[100] ccccccc............
        TarStream.arrayCopy(filename.encode(TarStream._encoding), header, 0)
        
        # 1-2. 권한
        # 100[  8] 0000nnn.
        mode = stat.st_mode
        header[100] = TarStream.ZERO
        header[101] = TarStream.ZERO
        header[102] = TarStream.ZERO
        header[103] = 0x30 | ((mode >> 6) & 0x07)
        header[104] = 0x30 | ((mode >> 3) & 0x07)
        header[105] = 0x30 | ((mode >> 0) & 0x07)
        header[106] = TarStream.SPACE
        header[107] = TarStream.NULL
        
        # 1-3. UID
        # 108[  8] ooooooo.
        TarStream.arrayCopy("{0:06o} ".format(stat.st_uid).encode(), header, 108)
        
        # 1-4. GID
        # 116[  8] ooooooo.
        TarStream.arrayCopy("{0:06o} ".format(stat.st_gid).encode(), header, 116)
        
        # 1-5. SIZE
        # 124[ 12] ooooooooooo.
        TarStream.arrayCopy("{0:011o} ".format(stat.st_size).encode(), header, 124)
        
        # 1-6. Modified time 
        # 136[ 12] nnnnnnnnnn0.
        TarStream.arrayCopy("{0:011o} ".format(int(stat.st_mtime)).encode(), header, 136)
        
        # 1-7. Check Sum dummy
        # 148[  8] ________ : 1-F 에서 재 정의
        TarStream.arrayFill(header, 0x20, 148, 8)
        
        # 1-8. Type flag
        # 156[  1] n : Normal = 0, Linked = 1, Symbolic = 2, Directory = 5
        header[156] = 0x30  # 일단은 Normal File 만.
        
        # 1-9. USTAR / Version indicator
        # 257[  6] ustar. 
        # 263[  2] 00
        TarStream.arrayCopy("ustar".encode(TarStream._encoding) , header, 257)
        TarStream.arrayCopy("00".encode(TarStream._encoding)    , header, 263)
        
        # 1-A. UNAME
        # 265[ 32] cccccc......
        TarStream.arrayCopy("THS".encode(TarStream._encoding), header, 265)
        
        # 1-B. GNAME
        # 297[ 32] cccccc......
        TarStream.arrayCopy("THS".encode(TarStream._encoding), header, 297)
        
        # 1-C. Device Major Number
        # 329[  8] nnnnnnn. 
        TarStream.arrayCopy("{0:06o} ".format(0).encode(), header, 329)
        
        # 1-D. Device Minor Number
        # 337[  8] nnnnnnn. 
        TarStream.arrayCopy("{0:06o} ".format(0).encode(), header, 337)
        
        # 1-E. Prefix 
        # 345[155] ccccccc.......
        # 미구현
        
        # 1-F. Header Checksum 계산
#         checksum = calc_chksums(header)[0]
        checksum = 0
        for c in header :
            checksum = checksum + c
        TarStream.arrayCopy("{0:06o}\0".format(checksum).encode(), header, 148) 
        
        # 1-X. Size 변경
        self._size = self._size + TarStream.BLOCK_SIZE # 헤더 추가
        self._size = self._size + TarStream.BLOCK_SIZE * math.ceil(stat.st_size / TarStream.BLOCK_SIZE)
        
        # 2. 파일리스트 추가
        # 2-1. 헤더 추가
        tarHeader = TemporaryFile()
        tarHeader.write(header)
        tarHeader.seek(0) 
        self._filelist.append(tarHeader)
        # 2-2. 파일 본문 추가
        file.seek(0)
        self._filelist.append(file)

    def getTarSize(self):
        return self._size
                        
    def __iter__(self):
        if self._filelist.__len__() == 0 :
            raise AssertionError("대상이 없잖어 대상이!")
        
        # 3. Null Block 추가
        for i in range(0, 2) :
            nullBlockFile = TemporaryFile()
            nullBlockFile.write(bytes(TarStream.BLOCK_SIZE))
            nullBlockFile.seek(0)
            self._filelist.append(nullBlockFile)
        
        self._iter_file = self._filelist.__iter__()
        self._currentFile = self._iter_file.__next__()
        self._EOS = False
        
        return self
    
    def __getitem__(self, key):
        # 지원하지 않음
        raise IndexError
#         block = self._currentFile.read(TarStream.BLOCK_SIZE)
#         if block.__len__() <= 0 :
#             self._currentFile.close()
#             self._currentFile = self._iter_file.__next__()
#             self._currentFile.seek(0)
#             return self.__getitem__(key)
#         
#         if block.__len__() < TarStream.BLOCK_SIZE :
#             dummy = bytearray(TarStream.BLOCK_SIZE)
#             TarStream.arrayCopy(block, dummy, 0)
#             block = dummy
#         
#         return block
    
    def __next__(self):
        block = self._currentFile.read(TarStream.BLOCK_SIZE * self._blocks)
        blocksize = len(block)
        if blocksize <= 0 :
            self._currentFile.close()
            self._currentFile = self._iter_file.__next__()
            if self._currentFile == None :
                raise StopIteration
            else :
                return self.__next__()
           
        if blocksize % TarStream.BLOCK_SIZE != 0 :
            dummy = bytearray(math.ceil(blocksize / TarStream.BLOCK_SIZE) * TarStream.BLOCK_SIZE)
            TarStream.arrayCopy(block, dummy, 0)
            block = bytes(dummy)
           
        return block
    
#     def __next__(self):
#         block = self._currentFile.read(TarStream.BLOCK_SIZE)
#         if block.__len__() <= 0 :
#             self._currentFile.close()
#             self._currentFile = self._iter_file.__next__()
#             if self._currentFile == None :
#                 raise StopIteration
#             else :
#                 return self.__next__()
#            
#         if block.__len__() < TarStream.BLOCK_SIZE :
#             dummy = bytearray(TarStream.BLOCK_SIZE)
#             TarStream.arrayCopy(block, dummy, 0)
#             block = bytes(dummy)
#            
#         return block

#     def __next__(self):
#         blocks = bytearray(TarStream.BLOCK_SIZE * self._blocks)
#         for i in range(0, self._blocks) :
#             block = self._getNextBlock() 
#             if block :
#                 TarStream.arrayCopy(block, blocks, i * TarStream.BLOCK_SIZE)
#         
#         if len(blocks) :                
#             return bytes(blocks)
#         else :
#             raise StopIteration
            
#     def _getNextBlock(self) :
#         block = self._currentFile.read(TarStream.BLOCK_SIZE)
#         if block.__len__() <= 0 :
#             self._currentFile.close()
#             self._currentFile = self._iter_file.__next__()
#             if self._currentFile == None :
#                 return None
#             else :
#                 return self._getNextBlock()
#           
#         if block.__len__() < TarStream.BLOCK_SIZE :
#             dummy = bytearray(TarStream.BLOCK_SIZE)
#             TarStream.arrayCopy(block, dummy, 0)
#             block = bytes(dummy)
#           
#         return block