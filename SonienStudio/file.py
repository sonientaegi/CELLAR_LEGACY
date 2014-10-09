import os
import shutil

os.path._normpath = os.path.normpath
os.path.normpath = lambda path : os.path._normpath(path).replace("\\", "/")
		
class FileManager :
	def __init__(self, root = "/") :		
		if(os.path.isdir(root)) :
			self._root 		= root
			self._root_norm	= os.path.normpath(root)
		else :
			raise AssertionError(root + " is not a directory")
		
	def isValidDir(self, dirPath) :
		"""
		입력한 디렉토리의 Validity 를 검증하고, 전체경로를 반환한다.
		return True, full path 	: 정상
		return False, 	None	: 경로가 잘못 지정되었습니다.
		"""
		
		fullPath = self._root + dirPath
		if not os.path.isdir(fullPath) :
			return False, None
		else : 
			return True, fullPath
	
	def getFileList(self, path = "/") :
		"""
		지정한 디렉토리의 하위 디렉토리와 파일 리스트를 이름순 대로 정렬하여 반환한다.
		return	: None 또는 ([디렉토리], [파일])
		디렉토리	: [ (basename, root 기준 상대 경로), ... ]
		파일		: [ (basename, root 기준 상대 경로, size), ... ] 
		"""
		listDir 	= []
		listFile	= []
		
		isValid, targetPath = self.isValidDir(path)
		if not isValid :
			return None
			
		if os.path.abspath(targetPath) != os.path.abspath(self._root) :
			# upPath = os.path.normpath(os.path.join(path, "..")) # self.join(path, "..")
			#if os.sep == "\\" :
			#	upPath = upPath.replace('\\', '/')
			pathParent = os.path.normpath(os.path.join(path, ".."))
			if pathParent != "/" :
				pathParent += "/" 
				
			listDir.append(("..", pathParent))
		
		for file in os.listdir(targetPath) :
			fullPath = os.path.join(targetPath, file)
			subPath  = os.path.normpath(os.path.join(path, file))
			#if os.sep == "\\" :
			#	subPath = subPath.replace('\\', '/')
	
			if os.path.isdir(fullPath) :
				listDir.append((file, subPath + "/"))
			else :
				listFile.append((file, subPath, os.path.getsize(fullPath)))
		return sorted(listDir, key = lambda path : path[0]), sorted(listFile, key = lambda file : file[0])
	
	def groupFileList(self, fileList):
		"""
		getFileList 로 추출한 파일 목록을 그룹핑 한다.
		return	: ([디렉토리], [파일])
		디렉토리	: (basename, root 기준 상대 경로)
		파일		: (basename, root 기준 상대 경로, [(확장자, root 기준 상대 경로, size)])  
		"""
		if fileList == None :
			raise AssertionError("File list must not be None")
			
		fileGroup = {}
		for file in fileList[1] :
			name, ext = os.path.splitext(file[0])
			if not name in fileGroup :
				fileGroup[name] = (os.path.splitext(file[1])[0], [])
			fileGroup[name][1].append((ext, file[1], file[2]))
			
		fileGroupArray = []
		for key in fileGroup.keys() :
			fileGroupArray.append((key, fileGroup[key][0], fileGroup[key][1]))
			
		return fileList[0], sorted(fileGroupArray, key = lambda record : record[0])
		
	def getFileGroup(self, dirPath = "/") :
		"""
		지정한 디렉토리의 하위 디렉토리와 파일 리스트를 정렬하여 반환한다.
		return	: None 또는 ([디렉토리], [파일])
		디렉토리	: (basename, root 기준 상대 경로)
		파일		: (basename, root 기준 상대 경로, [(확장자, root 기준 상대 경로, size)])  
		"""
		
		fileList = self.getFileList(dirPath)
		if fileList == None :
			return None
		
		return self.groupFileList(fileList)
		
	def rename(self, src, dst):
		"""
		파일 또는 경로의 이름을 변경한다.
		성공 시  		0
		src 미존재  		1
		dst 존재  		2
		상위 경로 접근	3
		그 외			4
		"""
		
		fullSrc = self._root + src
		normFullSrc = os.path.normpath(fullSrc)
		fullDst = self._root + dst
		normFullDst = os.path.normpath(fullDst) 
		
		if not os.path.exists(fullSrc) :
			return 1
		elif os.path.exists(fullDst) :
			return 2
		elif normFullSrc == self._root_norm or os.path.commonprefix([normFullSrc, normFullDst, self._root]) != self._root :
			return 3
		else :
			try :
				os.rename(fullSrc, fullDst)
				return 0
			except OSError as err :
				print(err)
				return 4
		
	def rmfile(self, filepath):
		"""
		파일을 삭제한다.
		성공 시		  		0
		대상이 경로일 시		1
		상위 경로 접근		3
		그 외				4
		"""
		
		fullPath = self._root + filepath
		normFullPath = os.path.normpath(fullPath)
		
		if not os.path.isfile(fullPath) :
			return 1
		elif os.path.commonprefix([normFullPath, self._root]) != self._root :
			return 3
		else :
			try :
				os.remove(fullPath)
				return 0
			except OSError as err :
				print(err)
				return 4
	
	def rmdir(self, dirPath):
		"""
		지정한 경로와 그 하위 항목을 모두 삭제한다.
		성공 시		  				0
		대상이 파일일 시			1
		루트 또는 상위 경로 접근	3
		그 외						4
		"""
		
		fullPath = self._root + dirPath
		normFullPath = os.path.normpath(fullPath)
		
		if not os.path.isdir(fullPath) :
			return 1
		elif normFullPath == self._root_norm or os.path.commonprefix([normFullPath, self._root]) != self._root :
			return 3
		else :
			try :
				shutil.rmtree(fullPath)
				return 0
			except OSError as err :
				print(err)
				return 4
			
	def  mkdir(self, parentPath, dirName):
		"""
		지정한 경로로 신규 디렉토리를 생성한다.
		성공 시					0
		부모 경로 미존재 시		1
		부모가 파일일 시		2
		생성 대상이 기 존재 시	3
		그 외					4
		"""
		newPath = self._root + parentPath + dirName
		if not os.path.exists(self._root + parentPath) :
			return 1
		elif os.path.isfile(self._root + parentPath) :
			return 2
		elif os.path.commonprefix([os.path.normpath(newPath), self._root]) != self._root :
			return 3
		else :
			try :
				os.mkdir(newPath)
				return 0
			except OSError as err :
				print(err)
				return 4
		
	def move(self, target, dst):
		"""
		파일 또는 경로의 이름을 변경한다.
		성공 시  		0
		src 미존재  	1
		dst 파일   		2
		상위 경로 접근	3
		그 외			4
		"""
		
		fullPathTarget 	= self._root + target
		fullPathDst		= self._root + dst
		
		
		if os.path.isfile(fullPathDst) :
			return 2
		
		if os.path.commonprefix([fullPathDst, self._root]) != self._root :
			return 3

		if not os.path.exists(fullPathTarget) :
			return 1
		
		try :
			shutil.move(os.path.normpath(fullPathTarget), fullPathDst)
			return 0
		except OSError as err :
			print(err)
			return 4		
	
	def isReadable(self, subPath):
		return True
	
	def _getDirChildren(self, subPath, current_depth, depth_to, sortRule = None):
		fullPath = self._root + subPath;		
		for child in os.listdir(fullPath) :
			subChild 	= subPath + child + "/";
			fullChild 	= fullPath + child;
			
			try :
				if os.path.isfile(fullChild) or not self.isReadable(subChild) : 
					continue			
				
				if depth_to == 0 or current_depth < depth_to - 1:
					yield child, subChild, sorted(list(self._getDirChildren(subChild, current_depth + 1, depth_to, sortRule)), key = sortRule) 
				else :
					yield child, subChild, []					
			except :
				continue

	def getDirTree(self, path = "/", depth_to = 0, sortRule = lambda child : child[0]) :
		""" 
		지정한 경로로 부터 하위 디렉토리를 반환한다. 
		None 또는
		[ (basname, root 기준 상대경로, 하위[...]), ... ]
		"""
		if not self.isValidDir(path)[0] :
			return None
		else :
			subPath = path
			return sorted(list(self._getDirChildren(subPath, 0, depth_to, sortRule)), key = sortRule)
	@staticmethod
	def getParent(path):
		return os.path.normpath(path + os.path.sep + os.pardir) + "/"
		# return os.path.abspath(os.path.join(path, os.pardir))
				
# 	@staticmethod
# 	def join(path, *paths) : 
# 		newPath = os.path.join(path, *paths)
# 		if os.path.sep != "/" :
# 			newPath = newPath.replace(os.path.sep, "/")
# 			
# 		return newPath
	
