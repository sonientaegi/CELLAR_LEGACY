var Filelist = {
	// filelist DOM 인스턴스
	instance 	: $("#table-filelist"),
	
	cwd		 	: "",
	readable 	: false,
	writeable	: false,
	deletable	: false,
	
	// type 0 : directory
	// type 1 : file
	render : function(type, data) {
		var row = $("<tr>");

		switch (type) {
		case 0:
			var target = "/" + data[0] + "/";
			
			var hierarchy = target.split("/");
			if (data[0] == "..") {
				target = target.substring(0, target.length - 4
						- hierarchy[hierarchy.length - 3].length) + "/";
			} else if (data[0] == ".") {
				target = target.substring(0, target.length - 2);
			}

			$('<td><img src="/static/img/folder.png" height="32" width="32"></td>').appendTo(row);
			$('<td><span id="dirname">' + data[0] + '</span></td>').appendTo(row);
			$('<td>').appendTo(row);
			$('<td>').appendTo(row);
			
			var browseDirectory = function() {
				Filelist.onClickDirectory(data[1]);
			};
			row.mouseenter(function() {
				row.css("cursor", "pointer");	
			});
			row.mouseleave(function() {
				row.css("cursor", "default");
			});
			row.click(browseDirectory);
			break;
		case 1:
			$("<td>").appendTo(row);
			$("<td><span id='filename'>" + data[0] + "</span></td>").appendTo(row);
			var tdSize = $("<td>");
			var tdExt = $("<td id='exts'>"); // style='max-width : 180px; min-width: 60px;'
			var size = 0;
			for (var i = 0; i < data[2].length; i++) {
				ext = data[2][i];
				var extName = ext[0];
				if (extName == "") {
					extName = "DOWN";
				}
				var button = $('<a id="ext" data-ajax="false">' + extName + "</a>");
				button.attr("href", "/download" + data[2][i][1]);
				button.data("ext", data[2][i][0]);
				button.click(function() {
					Filelist.onClickExt(ext);
				});
				button.appendTo(tdExt);
				button.addClass("ui-btn");
				button.addClass("ui-mini");
				button.addClass("ui-btn-inline");
				button.addClass("ui-shadow");
				button.css("min-width", "40px");
				
				size += ext[2];
			}
			tdSize.text(Sonien.getFileSizeString(size));

			tdSize.appendTo(row);
			tdExt.appendTo(row);
			break;
		}
		row.addClass("ui-mini");
		return row;
	},
	
	evaluator : function(data) {
		return data[1][1];
	},

	// filelist 의 내용을 갱신한다.
	browse : function(dir) {
		$.mobile.loading("show", {
				text : "Browsing...",
				textVisible : true
			}
		);
		
		$.post("/browse/filelist", {
			csrfmiddlewaretoken : '{{csrf_token}}',
			target : dir
		},
		function(data, status) {
			Filelist.fill(dir, JSON.parse(data));			
			$.mobile.loading("hide");
		});
	},
	
	fill : function(dir, jsonResponse) {
		Filelist.instance.tableHelper("remove-all");
		Filelist.instance.tableHelper("auto-sort", false);
		var directory = jsonResponse["directory"];
		var file = jsonResponse["file"];
		for (var i = 0; i < directory.length; i++) {
			Filelist.instance.tableHelper("append", [ 0, directory[i] ]);
		}

		for (var i = 0; i < file.length; i++) {
			Filelist.instance.tableHelper("append", [ 1, file[i] ]);
		}
		Filelist.instance.tableHelper("auto-sort", true);
		
		Filelist.cwd = dir;
		Filelist.readable 	= jsonResponse["readable"];
		Filelist.writeable	= jsonResponse["writeable"];
		Filelist.deletable	= jsonResponse["deletable"];
	},
	
	// type 0 : directory
	// type 1 : file
	// null   : both
	get : function(type) {
		type = type || 2;
		var data = [];
		var files = WidgetHelper.getData(Filelist.instance);
		for(var i = 0; i < files.length; i++) {
			if(type == 2 || files[i][0][0] == type ) {
				data.push(files[i][0][1]);
			}
		}
		
		return data;
	},
	
	del : function(target, exts) {
		if(exts == null) {
			Filelist.instance.tableHelper("remove", target);
		}
		else {
			var row = Filelist.instance.tableHelper("find", target);
			if(row == null)	return;
			
			var data  	= WidgetHelper.getData(row);
			if(data == null || data[0] == 0) return;
			
			for(var i = 0; i < exts.length; i++) {
				if(exts[i][1] != 0)	{
					continue;
				}
				
				var index = Sonien.binarySearch(data[1][2], exts[i][0], function(value) { return value[0]});
				data[1][2].splice(index, 1);
				row.find("#ext").each(function(index, element) {
					var elem = $(element);
					if(elem.data("ext") == exts[i]) {
						row.remove(elem);
						
					}
				});
			}
			
			if(data[1][2].length == 0) {
				Filelist.instance.tableHelper("remove", target);
			}
		}
	},
	
	add : function(data) {
		// 일단 디렉토리만 구현
		if(data[0] != 0) {
			return;
		}
		
		var countOfDir = 0;
		WidgetHelper.getData(Filelist.instance).forEach(function(rowData) {
			if(rowData[0][0] == 0) countOfDir++;
		});
		
		Filelist.instance.tableHelper("append", data, countOfDir);
	},

	// 디렉토리 링크 클릭시 행동을 정의
	_onClickDirectoryListener : null,
	setOnClickDirectoryListener : function(listener) {
		Filelist._onClickDirectoryListener = listener
	},
	onClickDirectory : function(targetDir) {
		if (Filelist._onClickDirectoryListener != null) {
			Filelist._onClickDirectoryListener(targetDir);
		} else {
			Filelist.browse(targetDir);
		}
	},

	// 확장자 버튼을 클릭 콜백 정의 : function(ext, size, path)
	_callbackClickExt : null,
	setCallbackClickExt : function(cb) {
		Filelist._callbackClickExt = cb;
	},
	onClickExt : function(targetFile) {
		if (Filelist._callbackClickExt != null) {
			Filelist._callbackClickExt(targetFile[0], targetFile[1], targetFile[2]);
		}
	},
	
	// Drag 를 시작할때 콜백 정의
	_onDragStart : null,
	setOnDragStartListener : function(listener) {
		Filelist._onDragStart = listener;
	},
	
	// Row 생성 시 콜백 정의 
	_callbackCreateRow : function(row, data, table) {
		if(data[0] == 1) {
			row.addClass("context_menu_filelist_file");
		}
		else if(data[1][0] != "..") {
			row.addClass("context_menu_filelist_dir");
		}
		
		row.attr("draggable", true);
		row.on("dragstart", function(event) {
			if(Filelist._onDragStart != null) {
				Filelist._onDragStart(event, row);
			}
		});
	},
	
	_callbackChangeDirName : function(code, srcPath, dst, dstPath){
		// ROW 찾기
		var row = Filelist.instance.tableHelper("find", srcPath);
		if(row == null) return;
		
		var data = WidgetHelper.getData(row);
		if(code == 0) {
			row.find("#dirname").first().text(dst);
			data[1][0] = dst;
			data[1][1] = dstPath;
			
			Filelist.instance.tableHelper("sort");
		}
		else {
			row.find("#dirname").first().text(data[1][0]);
		}
	},
	
	_callbackChangeFileGroupName : function(code, srcGroup, dst, dstGroup) {
		if(code == 0) {
			var row = Filelist.instance.tableHelper("find", srcGroup);
			if(row != null) {
				row.find("#filename").first().text(dst);
				var data = WidgetHelper.getData(row);
				data[1][0] = dst;
				data[1][1] = dstGroup;
				var exts = row.find("#exts > a").toArray();
				for(var i = 0; i < exts.length; i++) {
					var elem = $(exts[i]);
					elem.attr("href", "/download" + dstGroup + elem.data("ext"));
				}
				Filelist.instance.tableHelper("sort");
			}
		}
		else {
			Filelist.browse(Filelist.cwd);	
		}
	},
	
	_callbackMoveDir : function(code, targetPath, dstPath, newPath) {
		if(code != 0) {
			return;
		}
		
		if(dstPath == Filelist.cwd) {
			var dirName = newPath.slice(dstPath.length, newPath.length - 1);
			var data = [0, [dirName, newPath]];
			Filelist.add(data);
		}
		else {
			Filelist.del(targetPath);	
		}
	},
	
	_callbackMoveFile : function(code, targetGroup, dstPath, result) {
		if(code == 0) {
			Filelist.del(targetGroup);
		}
		else {
			Filelist.browse(Filelist.cwd);
		}
	},
	
	_callbackCreateDir : function(code, parentPath, dirName, newPath) {
		if(code != 0) {
			return;
		}
		
		if(parentPath == Filelist.cwd) {
			Filelist.add([0, [dirName, newPath]]);
		}
	},
	
	_callbackDeleteDir : function(code, targetPath) {
		if(code != 0) {
			return;
		}
		
		Filelist.del(targetPath);
	},
	
	_callbackDeleteFiles : function(code, groupPath, exts) {
		if(code != 0) {
			return;
		}
		
		Filelist.del(groupPath, exts);
	},
	
	ContextMenu_dir : {
	    selector : '.context_menu_filelist_dir', 
	    build : function($trigger, e) {
	    	var contextMenuItems = {};
	    	
	    	if(Filelist.writeable) {
	    		contextMenuItems["rename"] = {name: "이름 변경"};
	    	}
	    	
	    	if(Filelist.deletable) {
	    		contextMenuItems["delete"] = {name: "삭제"};
	    	}
	    	
	    	// {% if isAdmin %} 
	    	contextMenuItems["Seperator"] 	= "----";
	    	contextMenuItems["auth_read"] 	= {name: "읽기 권한"};
	    	contextMenuItems["auth_write"] 	= {name: "쓰기 권한"};
	    	contextMenuItems["auth_delete"] = {name: "삭제 권한"};
   			// {% endif %}

			return {
				items : contextMenuItems,
				callback : Filelist._callbackContextMenu_dir
			}
	    }
	},
	
	_callbackContextMenu_dir : function(key, options) {
		var data = WidgetHelper.getData(this);
		switch(key) {
		// {% if isAdmin %}
		case "auth_read" 	:
		case "auth_write"	:
		case "auth_delete"	:
			var auth_type = 0;
			if(key == "auth_read") {
				auth_type = 4
			}
			else if(key == "auth_write") {
				auth_type = 2;
			}
			else if(key == "auth_delete") {
				auth_type = 1;
			}
			
			$( ":mobile-pagecontainer" ).pagecontainer("change", "/auth/manager", { 
				type		: "post",
				data		: { path 				: data[1][1], 
								auth_type 			: auth_type,
								csrfmiddlewaretoken : '{{csrf_token}}' },
				role		: "dialog",
				transition	: "flip",
				closeBtn	: "right"
			});
			break;
		// {% endif %}
		case "delete" :
			popupYesNo.modal(
				"확인",
				"정말 지우시겠습니까?",
				data[1][0],		
				function() { 
					Transaction.deleteDir(data[1][1]); 
				}
			);
			break;
		case "rename" :
			popupFormText.modal(
				function(newDirName) {
					if(newDirName == "" || newDirName == data[1][0]) {
						return;
					}
					
					Transaction.changeDirName(data[1][1], newDirName);
				}, 
				true, 
				data[1][0]);
			break;
		}
	},
	
	ContextMenu_file : {
	    selector : '.context_menu_filelist_file', 
	    build : function($trigger, e) {
	    	var items = {};
	    	
	    	if(Filelist.writeable) {
	    		items["rename"] = {name: "이름 변경"};
	    	}
	    	
	    	if(Filelist.deletable) {
	    		items["delete"] = {name: "삭제"};
	    	}
	    	
			return {
				items : items,
				callback : Filelist._callbackContextMenu_file
			}
	    }
	},
	
	_callbackContextMenu_file : function(key, options) {
		var data = WidgetHelper.getData(this);
		switch(key) {
		case "delete" :
			popupYesNo.modal(
				"확인",
				"정말 지우시겠습니까?",
				data[1][0],		
				function() { 
					var exts = [];
					data[1][2].forEach(function(value) {
						exts.push(value[0]);
					});
					Transaction.deleteFiles(data[1][1], exts); 
				}
			);
			break;
		case "rename" :
			popupFormText.modal(
				function(newFileName) {
					if(newFileName == "" || newFileName == data[1][0]) {
						return;
					}
						
					var exts = [];
					for(var i = 0; i < data[1][2].length; i++) {
						exts.push(data[1][2][i][0]);
					}
					Transaction.changeFileGroupName(data[1][1], exts, newFileName);
				}, 
				true, 
				data[1][0]);
			break;
		}
	}
};