var CELLAR = {
	cwd : "/",
	
	isDirectreeLoaded	: false,
	isFilelistLoaded	: false,
	initial_browse : function() {
		Blocker.acquire("초기화 중...");
		if(!CELLAR.isDirectreeLoaded || !CELLAR.isFilelistLoaded) return;
		
		$.post("/browse", {
			csrfmiddlewaretoken : crsf_token,
			target : "/"
		},
		function(data, status) {
			if(status != 'success') {
				alert("초기화에 실패하였습니다. 새로 고침 해보세요.");
			}
			else {
				var jsonResponse = JSON.parse(data);
				Filelist.fill("/", jsonResponse["filelist"]); 
				Directree.fill("/", jsonResponse["directree"]);
				
				if(jsonResponse["directree"]["node"].length > 0) {
					var node = Directree.instance.treeHelper("find", "/");
					node.nodeHelper("expand", true);
				}
				CELLAR.cwd = "/";
				$("#field_cwd").text(CELLAR.cwd);
			}
			Blocker.reset();
		});
	},
	
	browse : function(dir) {
		Blocker.acquire("여는 중...");
		$.post("/browse", {
			csrfmiddlewaretoken : crsf_token,
			target : dir
		},
		function(data, status) {
			if(status != 'success') {
				alert("경로 열기에 실패하였습니다. 새로 고침 후 다시 시도해보세요.");
			}
			else {
				var jsonResponse = JSON.parse(data);
				Filelist.fill(dir, jsonResponse["filelist"]); 
				Directree.fill(dir, jsonResponse["directree"]);
				
				if(jsonResponse["directree"]["node"].length > 0) {
					var node = Directree.instance.treeHelper("find", dir);
					node.nodeHelper("expand", true);
				}
				CELLAR.cwd = dir;
				$("#field_cwd").text(CELLAR.cwd);
			}
			Blocker.release();
		});
	},
	
	toggleDirectory : function() {
		$("#panel_left").panel("toggle");
	},
	
	toggleMenu : function() {
		$("#panel_right").panel("toggle");
	},	

	popupNewDirectory : function() {
		popupFormText.modal(function(newDirName) {
			Transaction.createDir(CELLAR.cwd, newDirName);	
		});
	},
	
	popupUploader : function() {
		window.history.pushState({needRefresh : true} , "", "/module/upload");
		CELLAR.toggleMenu();
		$( ":mobile-pagecontainer" ).pagecontainer("change", "/module/upload", { 
			type		: "post",
			data		: { cwd 				: CELLAR.cwd, 
							csrfmiddlewaretoken : '{{csrf_token}}' },
			role		: "dialog",
			transition	: "slidedown",
			closeBtn	: "right"
		});
	},
	
	dragStart_directree : function(event, node) {
		var data = WidgetHelper.getData(node);
		var target = [0, data[0][1], data[0][0]];
		event.originalEvent.dataTransfer.setData("text", JSON.stringify(target));
	},
	
	dragStart_filelist : function(event, row) {
		var data = WidgetHelper.getData(row);
		var target = null;
		
		switch(data[0]) {
		case 0 :
			target = [data[0], data[1][1], []];
			break;
		case 1 :
			var exts = [];
			data[1][2].forEach(function(extData) {
				exts.push(extData[0]);
			});
			target = [data[0], data[1][1].slice(0, data[1][1].length - data[1][0].length), data[1][0], exts];
			break;
		}
		
		event.originalEvent.dataTransfer.setData("text", JSON.stringify(target));
	},
	
	/*
	 * [유형, 식별자, [자식]]
	 */
	dropOn_directree : function(event, node) {
		event.preventDefault();
		var dstPath		= WidgetHelper.getData(node)[0][1];
		var targetData 	= event.originalEvent.dataTransfer.getData("text"); 
		if(targetData == null || targetData == "") {
			return false;
		}
		
		var target 		= JSON.parse(targetData);
		if(target[0] == 0) {
			// 디렉토리 인 경우, 자기 자신 과 Parent 가 아닌 경우에만 이동 함.	
			if(dstPath != target[1] && !node.nodeHelper("findChild", dstPath + target[2] + "/") && node.nodeHelper("findParent", target[1]) == null) {
				Transaction.moveDir(target[1], dstPath);
			}
		}
		else {
			// 파일 인 경우, 자기 자신이 위치하는 곳이 아닌 경우에만 이동 함.
			if(dstPath != target[1]) {
				Transaction.moveFile(target[1] + target[2] , target[3], dstPath);
			}
		}
	},
	
	dump_cwd : function() {
		var params	= "";
		var files	= Filelist.get(1);
		if(files.length == 0) {
			return;
		}
		var path	= CELLAR.cwd;
		params = 'csrfmiddlewaretoken=' + crsf_token;
		params = params + '&path=' + path;
		
		var target = [];
		for(var i = 0; i < files.length; i++) {
			var file = files[i];
			for(var j = 0; j < file[2].length; j++) {
				target.push(file[0] + file[2][j]);
				params = params + "&files[]=" + file[0] + file[2][j][0];
			}
		}
		
		var filename = "CELLAR.tar";
		var dirs = path.split("/");
		for(var i = dirs.length - 1; i >= 0; i--) {
		    if(dirs[i] == "") continue;
		    
		    filename = dirs[i] + ".tar";
		    break;
		}
		
		Sonien.download('/tarload/' + filename, params, 'post');
	},

	onPanelUpdate : function(event, ui) {
		if(Filelist.writeable) {
			$("#panel_right_newdir").show();
			$("#panel_right_upload").show();
		}
		else {
			$("#panel_right_newdir").hide();
			$("#panel_right_upload").hide();
		}
	}
};