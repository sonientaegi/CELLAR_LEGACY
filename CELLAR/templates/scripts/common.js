var Transaction = {
	_callbackChangeDirName 		: [],
	addCallbackChangeDirName	: function(cb) {
		Transaction._callbackChangeDirName.push(cb);
	},
	changeDirName : function(srcPath, dst) {
		Blocker.acquire();
		$.post("/util/rename",
			{ 
				csrfmiddlewaretoken : crsf_token, 
				srcPath : srcPath,
				dst 	: dst
			},
			function(data, status) {
				var jsonResponse = JSON.parse(data);
				for(var i = 0; i < Transaction._callbackChangeDirName.length; i++) {
					Transaction._callbackChangeDirName[i](jsonResponse["code"], srcPath, jsonResponse["dst"], jsonResponse["dstPath"]);
				}
				
				Blocker.release();
			}
		);	
	},
	
	_callbackChangeFileGroupName	: [],
	addCallbackChangeFileGroupName	: function(cb) {
		Transaction._callbackChangeFileGroupName.push(cb);
	},
	changeFileGroupName : function(srcGroup, srcExts, dst) {
		Blocker.acquire();
		$.post("/util/renamegroup",
			{ 
				csrfmiddlewaretoken : crsf_token, 
				srcGroup 	: srcGroup,
				srcExts		: srcExts,		
				dst 		: dst
			},
			function(data, status) {
				var jsonResponse = JSON.parse(data);
				for(var i = 0; i < Transaction._callbackChangeFileGroupName.length; i++) {
					Transaction._callbackChangeFileGroupName[i](jsonResponse["code"], srcGroup, dst, jsonResponse["dstGroup"]);
				}
				
				Blocker.release();
			}
		);
	},
	
	_callbackMoveDir 	: [],
	addCallbackMoveDir 	: function(cb) {
		Transaction._callbackMoveDir.push(cb);
	},
	moveDir : function(targetDir, dstPath) {
		Blocker.acquire();
		$.post("/util/move",
			{ 
				csrfmiddlewaretoken : crsf_token, 
				targets : [targetDir],
				dstPath : dstPath
			},
			function(data, status) {
				var jsonResponse = JSON.parse(data);
				var result = jsonResponse["result"][0];
				for(var i = 0; i < Transaction._callbackMoveDir.length; i++) {
					Transaction._callbackMoveDir[i](result[1], result[0], jsonResponse["dstPath"], result[2]);
				}
				Blocker.release();
			}
		);
	},
	
	_callbackMoveFile	: [],
	addCallbackMoveFile	: function(cb) {
		Transaction._callbackMoveFile.push(cb);
	},
	moveFile : function(targetGroup, targetExts, dstPath) {
		Blocker.acquire();
		var targets = [];
		for(var i = 0 ; i < targetExts.length; i++) {
			targets.push(targetGroup + targetExts[i]);
		}
		$.post("/util/move",
			{ 
				csrfmiddlewaretoken : crsf_token, 
				targets : targets,
				dstPath : dstPath
			},
			function(data, status) {
				var jsonResponse = JSON.parse(data);
				for(var i = 0; i < Transaction._callbackMoveFile.length; i++) {
					Transaction._callbackMoveDir[i](jsonResponse["code"], targetGroup, dstPath, jsonResponse["result"]);
				}
				Blocker.release();
			}
		);
	},
	
	_callbackCreateDir		: [],
	addCallbackCreateDir	: function(cb) {
		Transaction._callbackCreateDir.push(cb);
	},
	createDir : function(path, name) {
		Blocker.acquire();
		$.post("/util/createdir",
			{ 
				csrfmiddlewaretoken : crsf_token, 
				parentPath 	: path,
				dirName 	: name
			},
			function(data, status) {
				var jsonResponse = JSON.parse(data);
				var newPath = jsonResponse["newPath"];
				for(var i = 0; i < Transaction._callbackCreateDir.length; i++) {
					Transaction._callbackCreateDir[i](jsonResponse["code"], path, name, newPath);
				}
				Blocker.release();
			}
		);
	}, 
	
	_callbackDeleteDir		: [],
	addCallbackDeleteDir	: function(cb) {
		Transaction._callbackDeleteDir.push(cb);
	},
	deleteDir : function(dirPath) {
		Blocker.acquire();
		$.post("/util/deletedir",
			{ 
				csrfmiddlewaretoken : crsf_token, 
				dirPath 	: dirPath,
			},
			function(data, status) {
				var jsonResponse = JSON.parse(data);
				for(var i = 0; i < Transaction._callbackDeleteDir.length; i++) {
					Transaction._callbackDeleteDir[i](jsonResponse["code"], jsonResponse["dirPath"]);
				}
				Blocker.release();
			}
		);
	},
	
	_callbackDeleteFiles	: [],
	addCallbackDeleteFiles	: function(cb) {
		Transaction._callbackDeleteFiles.push(cb);
	},
	deleteFiles : function(groupPath, exts) {
		Blocker.acquire();
		$.post("/util/deletefiles",
			{ 
				csrfmiddlewaretoken : crsf_token, 
				groupPath 	: groupPath,
				exts 		: exts
			},
			function(data, status) {
				var jsonResponse = JSON.parse(data);
				for(var i = 0; i < Transaction._callbackDeleteFiles.length; i++) {
					Transaction._callbackDeleteFiles[i](jsonResponse["code"], jsonResponse["groupPath"], jsonResponse["result"]);
				}
				Blocker.release();
			}
		);
	}
};