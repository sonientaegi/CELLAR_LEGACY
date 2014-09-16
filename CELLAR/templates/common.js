var Transaction = {
	_callbackChangeDirName 		: [],
	addCallbackChangeDirName	: function(cb) {
		Transaction._callbackChangeDirName.push(cb);
	},
	changeDirName : function(srcPath, dst) {
		console.log("changeDirName : src=" + srcPath + " dst=" + dst);
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
				
				console.log("changeDirName : " + jsonResponse["message"]);
			}
		);	
	},
	
	_callbackChangeFileGroupName	: [],
	addCallbackChangeFileGroupName	: function(cb) {
		Transaction._callbackChangeFileGroupName.push(cb);
	},
	changeFileGroupName : function(srcGroup, srcExts, dst) {
		console.log("changeFileGroupName : src=" + srcGroup + " dst=" + dst);
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
				
				console.log("changeDirName : " + jsonResponse["message"]);
			}
		);
	},
	
	_callbackMoveDir 	: [],
	addCallbackMoveDir 	: function(cb) {
		Transaction._callbackMoveDir.push(cb);
	},
	moveDir : function(targetDir, dstPath) {
		console.log("moveDir : target=" + targetDir + " dstPath=" + dstPath);
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
				
				console.log("moveDir : " + jsonResponse["message"]);
			}
		);
	},
	
	_callbackMoveFile	: [],
	addCallbackMoveFile	: function(cb) {
		Transaction._callbackMoveFile.push(cb);
	},
	moveFile : function(targetGroup, targetExts, dstPath) {
		console.log("moveFile : target=" + targetGroup + "(" + targetExts + ") dstPath=" + dstPath);
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
				console.log("moveFile : " + jsonResponse["message"]);
			}
		);
	},
	
	_callbackCreateDir		: [],
	addCallbackCreateDir	: function(cb) {
		Transaction._callbackCreateDir.push(cb);
	},
	createDir : function(path, name) {
		console.log("createDir : " + path + name);
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
				console.log("createDir : " + jsonResponse["message"]);
			}
		);
	}, 
	
	_callbackDeleteDir		: [],
	addCallbackDeleteDir	: function(cb) {
		Transaction._callbackDeleteDir.push(cb);
	},
	deleteDir : function(dirPath) {
		console.log("deleteDir : " + dirPath);
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
				console.log("deleteDir : " + jsonResponse["message"]);
			}
		);
	},
	
	_callbackDeleteFiles	: [],
	addCallbackDeleteFiles	: function(cb) {
		Transaction._callbackDeleteFiles.push(cb);
	},
	deleteFiles : function(groupPath, exts) {
		console.log("deleteFiles : " + groupPath + " (" + exts + ")");
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
				console.log("deleteFiles : " + jsonResponse["message"]);
			}
		);
	}
};