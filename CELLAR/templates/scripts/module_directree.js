var Directree = {
	// directree DOM 인스턴스
	instance : $("#tree-directory"),
	root	 : null,
	
	render : function(title, path, children) {
		var node 	= this;
		var header 	= $("<h1>" + title + "</h1>");
		header.click(function(event) {
			if(event.offsetX <= setting.directree_toggle_size) {
				node.nodeHelper("toggle");
			}
			else {
				Directree._onClickDirectory(WidgetHelper.getData(node)[0][1]);
			}
		});
		
		return header;
	},
	
	evaluator : function(data) {
		return data[1]; // 사용자 root 기준 상대 경로
	},
	
	browse : function(dir) {		
		Blocker.acquire("Browsing ...");
		$.post("/browse/directory", {
				target				: dir,
				csrfmiddlewaretoken : '{{csrf_token}}'
			},
			function(data, status) {
				Directree.fill(dir, JSON.parse(data));
				Blocker.release();
			}
		);
	},
	
	fill : function(parent, jsonResponse) {
		var parentNode = Directree.instance.treeHelper("find", parent);
		var children = jsonResponse['node'];
		
		var nodes = Directree.instance.data("sonienNode");
		for(var i = 0; i < children.length; i++) {
			var childNode = parentNode.nodeHelper("addChild", children[i]);
			Directree._refresh(childNode);
		}
	},
	
	ContextMenu : {
	    selector : '.context_menu_directree', 
	    build : function($trigger, e) {	    	
	    	var contextMenuItems = {};
	    	// {% if isYeoman %}
	    	contextMenuItems["create"]	= {name: "새 폴더"};
	    	if(!$(e.currentTarget).hasClass("home_directory")) {
	    		contextMenuItems["rename"]	= {name: "이름 변경"};
	    		contextMenuItems["delete"]	= {name: "삭제"};
	    	}
	    	// {% endif %}
	    	// {% if isAdmin %} 
	    	contextMenuItems["Seperator"] 	= "----";
	    	contextMenuItems["auth_read"] 	= {name: "읽기 권한"};
	    	contextMenuItems["auth_write"] 	= {name: "쓰기 권한"};
	    	contextMenuItems["auth_delete"] = {name: "삭제 권한"};
   			// {% endif %}
	    	
			return {
				items 		: contextMenuItems, 
				callback 	: Directree._callbackContextMenu
			}
	    }
	},
	
	_callbackContextMenu : function(key, options) {
		var data = WidgetHelper.getData(this);
		switch(key) {
		// {% if isAdmin %} 	
		case "auth_read" 	:
		case "auth_write"	:
		case "auth_delete"	:
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
				data		: { path 				: data[0][1], 
								auth_type 			: auth_type,
								csrfmiddlewaretoken : '{{csrf_token}}' },
				role		: "dialog",
				transition	: "flip",
				closeBtn	: "right"
			});
			break;
		// {% endif %}
		// {% if isYeoman %}
		case "delete" :
			popupYesNo.modal(
				"확인",
				"정말 지우시겠습니까?",
				data[0][0],		
				function() { 
					Transaction.deleteDir(data[0][1]); 
				}
			);
			break;
		case "rename" :
			popupFormText.modal(
				function(newDirName) {
					if(newDirName == "" || newDirName == data[0][0]) {
						return;
					}
					Transaction.changeDirName(data[0][1], newDirName);
				}, 
				true, 
				data[0][0]);
			break;
		case "create" :
			popupFormText.modal(function(newDirName) {
				Transaction.createDir(data[0][1], newDirName);	
			});
			break;
		// {% endif %}
		}
	},
	
	_onDragStart : null,
	setOnDragStartListener : function(listener) {
		Directree._onDragStart = listener;
	},
	
	_onDragOver : function(event, node) {
		event.preventDefault();  
	},
	
	_onDrop : null,
	setOnDropListener : function(listener) {
		Directree._onDrop = listener;
	},
	
	_onClickDirectory : null,
	setOnClickDirectoryListener : function(listener) {
		Directree._onClickDirectory = listener;
	},
	
	_callbackCreate : function(node, data) {
		node.css("margin-top", "-1px");
		var header = node.find("h1").first();
		WidgetHelper.setData(header, WidgetHelper.getData(node));
		var childrenContainer = node.nodeHelper("childrenContainer");
		header.addClass("context_menu_directree");
	 	if(data[1] == "/") {
	 		header.addClass("home_directory");
	 		if(Directree.instance.collapsibleset("option", "inset") == false) {
	 			header.find("a").css("border-right", "0px");
	 			childrenContainer.parent().css("border-right", "0px");
	 		}
	 	}
	 	else {
			node.collapsible("option", "inset", false);
			node.collapsible("option", "corners", false);
			
		 	childrenContainer.parent().css("border-right", "0px");
			childrenContainer.parent().css("border-left", "0px");
	
			node.contents().first().contents().first().css("border-right", "0px");
		}
		childrenContainer.parent().css("border-bottom", "0px");
		childrenContainer.parent().css("background-color", "transparent");

		// {% if isYeoman %}
		// Drag and drop 구현			
		if(data[1] != "/") {
			// header.attr("draggable", true);
			header.prop("draggable", true);
			
			header.on("dragstart", function(event) {
				if(Directree._onDragStart != null) {
					Directree._onDragStart(event, node);
				}
			});
			
			/*
			 * Will be implemented in the future.
			header.on("dragend", function(event) {
			});
			*/
		}
		
		header.on("dragover", function(event) {
			if(Directree._onDragOver != null) {
				Directree._onDragOver(event, node);
			}
		});
		
		header.on("drop", function(event) {
			if(Directree._onDrop != null) {
				Directree._onDrop(event, node);
			}
		});
		// {% endif %}
		
		childrenContainer.css("margin", "0px");
		childrenContainer.css("margin-left", "10px");
		childrenContainer.parent().css("padding", "0px");
		
		node.collapsible("option", "mini", true);			// mini 	: Collapsible 설정 
		node.collapsible("option", "inset", true);			// inset	: Collapsible 섧정
		node.collapsible("option", "expandedIcon", "minus");
		
		if(WidgetHelper.getData(node)[2].length == 0) {
			node.collapsible("option", "collapsedIcon", "na");
		}
	},
	
	_callbackAdd : function(node, data) {
		node.collapsible("option", "collapsedIcon", "plus");
	},
	
	_callbackRemove : function(parentNode, tree) {
		if(!parentNode.nodeHelper("hasChild")) {
			parentNode.collapsible("option", "collapsedIcon", "na");
			parentNode.nodeHelper("toggle");
		}
	},
	
	_callbackAttach : function(parentNode, node, tree) {
		parentNode.collapsible("option", "collapsedIcon", "plus");
		Directree._refresh(parentNode);
	},
	
	_callbackDetach : function(parentNode, node, tree) {
		if(!parentNode.nodeHelper("hasChild")) {
			parentNode.collapsible("option", "collapsedIcon", "na");
			parentNode.nodeHelper("toggle");
		}
	},
	
	_callbackChangeDirName : function(code, srcPath, dst, dstPath){
		// NODE 찾기
		var node = Directree.instance.treeHelper("find", srcPath);
		var data = WidgetHelper.getData(node);
		
		if(code == 0) {
			node.find("a").first().text(dst);
			data[0][0] = dst;
			data[0][1] = dstPath;
			
			Directree.updateDirectories(srcPath, dstPath);
		}
		else {
			node.find("a").text(data[0][0]);
		}
	},
	
	_callbackMoveDir : function(code, targetPath, dstPath, newPath) {
		if(code == 0) {
			var node 	= Directree.instance.treeHelper("find", targetPath);
			var parent	= Directree.instance.treeHelper("find", dstPath);
			
			Directree.updateDirectories(targetPath, newPath);
			if(node != null && parent != null) {
				node.nodeHelper("attachTo", parent);
			}
		}
	},
	
	_callbackCreateDir : function(code, parentPath, dirName, newPath) {
		if(code != 0) {
			return;
		}
		
		var parentNode = Directree.instance.treeHelper("find", parentPath);
		if(parentNode == null) {
			return;
		}
		
		var childNode = parentNode.nodeHelper("addChild", [dirName, newPath, []]);
		Directree._refresh(childNode);
	},
	
	_callbackDeleteDir : function(code, targetPath) {
		if(code != 0) {
			return;
		}
	
		var node 		= Directree.instance.treeHelper("find", targetPath);
		if(node == null) {
			return;
		}
		node.nodeHelper("parent").nodeHelper("removeChild", node);
	},
	
	_refresh : function(node) {
		var depth = node.nodeHelper("getDepth");
		var rgb = 155 - ( 100 * Math.pow(0.92, depth) ) | 0;
		node.find("h1").find("a").css("background-color", "rgb(" + rgb + "," + rgb + "," + rgb + ")");
		
		var children = node.nodeHelper("children");
		for(var i = 0; i < children.length; i++) {
			Directree._refresh(children[i][1]);
		}
	},
	
	updateDirectories : function(srcPath, dstPath) {
		var length = srcPath.length;
		var children = Directree.instance.data("sonienNode");
		for(var i = 0; i < children.length; i++) {
			if(children[i][0][1].indexOf(srcPath) == 0) {
				children[i][0][1] = dstPath + children[i][0][1].slice([length]);
			}
		}
		
		Directree.instance.treeHelper("sort");
	}
}