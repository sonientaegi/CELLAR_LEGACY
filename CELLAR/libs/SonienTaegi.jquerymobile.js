/* jquery mobile helper library by SonienTaegi */

/* Common Library */
var WidgetHelper = {
	equals : function(a, b) {
		var evaluator = WidgetHelper.getEvaluator(a);
		return evaluator(WidgetHelper.getData(a)) == evaluator(WidgetHelper.getData(b));
	},
	
	setData : function(widget, data) {
		widget.data("sonienData", data);
	},

	getData : function(widget) {
		return widget.data("sonienData");
	},
	
	templator : function() {
		container = arguments[0];
		if(arguments.length == 1) {
			return container.data("sonienTemplate");
		}
		else {
			return container.data("sonienTemplate", arguments[1]);
		}
	},
	
	// Data format of a widget
	// data[0] = Value data
	// data[1] = Widget itself
	// data[n] = expandable variables
	setEvaluator : function(widget, evaluator) {
		if(evaluator != null) {
			widget.data("sonienEvaluator", function(value) {
				return evaluator(value[0]);
			});
		}
		else {
			widget.data("sonienEvaluator", function(value) {
				return value[0];
			});
		}
	},	
	
	copyEvaluator : function(widget, evaluator) {
		widget.data("sonienEvaluator", evaluator);
	},
	
	getEvaluator : function(widget) {
		return widget.data("sonienEvaluator");
	}
};

var TreeHelper = {
	create : function(domDiv, template) {
		var tree = domDiv.collapsibleset();
		WidgetHelper.templator(tree, template);
		WidgetHelper.setEvaluator(tree, null);
		tree.data("sonienNode", []);
		
		TreeHelper.setToggling(tree, true);
		return tree;
	},
	
	_addNode : function(tree, node) {
		var nodes = tree.data("sonienNode");
		var data = WidgetHelper.getData(node);
		
		nodes.push(data);
		tree.data("sonienNode", nodes);
		TreeHelper.sort(tree);
	},
	
	_removeNode : function(tree, key) {
		var evaluator	= WidgetHelper.getEvaluator(tree);
		var nodes 		= tree.data("sonienNode");
		var index 		= Sonien.binarySearch(nodes, key, evaluator);
		
		if(index >= 0) {
			var children = nodes[index][2];
			nodes.splice(index, 1);

			// 재귀법으로 하위 노드도 모두 삭제
			for(var i = 0; i < children.length; i++) {
				TreeHelper._removeNode(tree, evaluator(children[i]));
			}
		}
	},
	
	sort : function(tree) {
		var nodes = tree.data("sonienNode");
		Quicksort.sort(nodes, WidgetHelper.getEvaluator(tree));
		tree.data("sonienNode", nodes);
	},
	
	findNode : function(tree, key) {
		var nodes = tree.data("sonienNode");
		var index = Sonien.binarySearch(nodes, key, WidgetHelper.getEvaluator(tree));
		if(index >= 0) {
			return nodes[index][1];
		}
		else {
			return null;
		}	
		return null;
	},
	
	addRoot : function(tree, data) {
		root = NodeHelper.create(tree, data);
		root.data("sonienRoot", true);
		root.data("sonienDepth", 0);
		tree.append(root);
		tree.collapsibleset('refresh');
		TreeHelper._addNode(tree, root);
		
		return root;
	},
	
	removeNode : function(tree, key) {
		var node = TreeHelper.findNode(tree, key);
		if(node != null) {
			node.remove();
			TreeHelper._removeNode(tree, key);
		}
	},
	
	setCallbackAddNode : function(tree, cb) {
		tree.data("sonienCbAddNode", cb);
		return tree;
	},
	
	getCallbackAddNode : function(tree) {
		return tree.data("sonienCbAddNode"); 
	},
	
	setCallbackRemoveNode : function(tree, cb) {
		tree.data("sonienCbRemoveNode");
		return tree;
	},
	
	getCallbackRemoveNode : function(tree) {
		return tree.data("sonienCbRemoveNode");
	},
	
	setCallbackCreateNode : function(tree, cb) {
		tree.data("sonienCbCreateNode", cb);
		return tree;
	},
	
	getCallbackCreateNode : function(tree) {
		return tree.data("sonienCbCreateNode");
	},
	
	setCallbackAttachNode : function(tree, cb) {
		tree.data("sonienCbAttachNode", cb);
		return tree;
	},
	
	getCallbackAttachNode : function(tree) {
		return tree.data("sonienCbAttachNode"); 
	},
	
	setCallbackDetachNode : function(tree, cb) {
		tree.data("sonienCbDetachNode", cb);
		return tree;
	},
	
	getCallbackDetachNode : function(tree) {
		return tree.data("sonienCbDetachNode"); 
	},
	
	setToggling : function(tree, enable) {
		tree.data("sonienToggling", enable);
		// 모든 자식 collasible enable / disable 로직 추가 필요
		return tree; 
	},
	
	isToggling : function(tree) {
		return tree.data("sonienToggling");
	}
};

/**
 * Format of Node Data
 * data[0] = Value data
 * data[1] = Node DOM
 * data[2] = Set of childish Node Data
 */
var NodeHelper = {
	create : function(tree, data) {
		// console.log("노드 생성 : " + data[0]);
		
		var templator 	= tree.data("sonienTemplate");
		var node 		= $("<div data-role='collapsible'></div>");
		var title 		= templator.apply(node, data);
		var children	= $("<div></div>");

		// children.collapsibleset();
		node.append(title);
		node.append(children);
		node.collapsible();		
		node.collapsible(TreeHelper.isToggling(tree) ? "enable" : "disable");
		node.data("sonienTree", tree);
		node.data("sonienChildren", children);
		WidgetHelper.setData(node, [[data[0], data[1]], node, []]);
		WidgetHelper.copyEvaluator(node, WidgetHelper.getEvaluator(tree));

		// 하위 개체 존재 시 재귀법으로 생성
		for(var i = 0; i < data[2].length; i++) {
			NodeHelper.addChild(node, data[2][i]);
		}
		
		var cbCreateNode = TreeHelper.getCallbackCreateNode(tree);
		if(cbCreateNode) {
			cbCreateNode(node, data, tree);
		}

		return node;
	},
	
	getTree : function(node) {
		return node.data("sonienTree");
	},
	
	getDepth : function(node) {
		return node.data("sonienDepth");
	},
	
	addChild : function(node, data) {
		// console.log("노드 추가 : " + data[0]);
		
		var tree 		= node.data("sonienTree");
		var child 		= null;
		
		// 기존 등록된 노드가 존재하는지 확인
		var existParent = null;
		var existChild 	= null;
		
		existChild = TreeHelper.findNode(tree, WidgetHelper.getEvaluator(node)([data]));
		if(existChild) {	
			// 기 등록된 노드가 존재 시 부모 노드를 구한다.
			existParent = NodeHelper.parent(existChild);
		}
	
		if(existChild == null) {
			// 미 존재시 추가한다.
			var child = NodeHelper.create(tree, data); 
			node.data("sonienChildren").append(child);
						
			nodeData 	= WidgetHelper.getData(node);
			childData 	= WidgetHelper.getData(child);
			nodeData[2].push(childData);
			
			var cbAddNode = TreeHelper.getCallbackAddNode(tree);
			if(cbAddNode) {
				cbAddNode(node, data, tree);
			}
			
			TreeHelper._addNode(tree, child);
			Quicksort.sort(nodeData[2], WidgetHelper.getEvaluator(node));
		}
		else if(WidgetHelper.equals(existParent, node)) {			
			// 부모가 Node 인 경우, 즉 자기 자신인 경우 재귀적으로 자식을 추가한다.
			child = existChild;
			for(var i = 0; i < data[2].length; i++) {
				NodeHelper.addChild(child, data[2][i]);
			}
		}
		
		// 부모 노드의 Depth 가 이미 정해진 경우, 즉 자식의 Depth 를 결정할 수 있을때 Depth 를 갱신해준다.
		if(node.data("sonienDepth") != null) {
			NodeHelper._refreshChildDepth(child);
		}
		
		return child;
	},
	
	toggle : function(node) {
		if(NodeHelper.isCollapsed(node)) {
			if(WidgetHelper.getData(node)[2].length > 0) {
				node.collapsible("expand");
				return true;
			}
			else {
				return false;
			}
		}
		else {
			node.collapsible("collapse");
			return true;
		}
	},
	
	expand : function(node, recursive) {
		recursive = recursive || false;
		
		node.collapsible("expand");
		if(recursive && !NodeHelper.isRoot(node)) {
			NodeHelper.expand(NodeHelper.parent(node));
		}
	},
	
	isCollapsed : function(node) {
		var hasClass = node.hasClass("ui-collapsible-collapsed"); 
		return hasClass;
	},
	
	/**
	 * Return Children Container for child nodes DOMs
	 */
	childrenContainer : function(node) {
		return node.data("sonienChildren");
	},
	
	/**
	 * Make clone of child node data set
	 */
	children : function(node) {
		var array = [];
		return WidgetHelper.getData(node)[2].slice(0);
	},
	
	hasChild : function(node) {
		var data = WidgetHelper.getData(node);
		console.log("hasChild " + data[2]);
		return data[2].length > 0;
	},
	
	parent : function(node) {
		if(NodeHelper.isRoot(node)) {
			return null;
		}
		else {
			return node.parent().parent().parent();
		}
	},
	
	isRoot : function(node) {
		return node.data("sonienRoot") || false;
	},
	
	_refreshChildDepth : function(node) {
		var parentNode = NodeHelper.parent(node);
		var nextDepth = parentNode.data("sonienDepth") + 1;
		node.data("sonienDepth", nextDepth);
		
		var childrenNode = NodeHelper.children(node);
		for(var i = 0; i < childrenNode.length; i++) {
			NodeHelper._refreshChildDepth(childrenNode[i][1]);
		}
	},
	
	_attach : function(parentNode, node) {		
		// debugger;
		node.appendTo(parentNode.data("sonienChildren"));
		var parentData 	= WidgetHelper.getData(parentNode);
		var nodeData	= WidgetHelper.getData(node);
		parentData[2].push(nodeData);
		Quicksort.sort(parentData[2], WidgetHelper.getEvaluator(parentNode));
		

		// 부모 노드의 Depth 가 이미 정해진 경우, 즉 자식의 Depth 를 결정할 수 있을때 Depth 를 갱신해준다.
		if(parentNode.data("sonienDepth") != null) {
			NodeHelper._refreshChildDepth(node);
		}
		
		var tree = NodeHelper.getTree(parentNode);
		var cbAttachNode = TreeHelper.getCallbackAttachNode(tree);
		if(cbAttachNode) {
			cbAttachNode(parentNode, node, tree);
		}
	},
	
	_detach : function(node) {		
		// debugger;
		var parentNode 	= NodeHelper.parent(node);
		var dataSet		= WidgetHelper.getData(parentNode)[2];
		var evaluator	= WidgetHelper.getEvaluator(parentNode);
		var index		= Sonien.binarySearch(dataSet, evaluator(WidgetHelper.getData(node)), evaluator);
		dataSet.splice(index, 1);
		node.detach();
		
		var tree = NodeHelper.getTree(parentNode);
		var cbDetachNode = TreeHelper.getCallbackDetachNode(tree);
		if(cbDetachNode) {
			cbDetachNode(parentNode, node, tree);
		}
	}
};

var TableHelper = {
	create 	: function(domTable, template) {
		var table = domTable.table();
		WidgetHelper.templator(table, template);
		WidgetHelper.setData(table, []);
		WidgetHelper.setEvaluator(table, null);
	},
	
	sort : function(table) {
		Quicksort.sort(WidgetHelper.getData(table), WidgetHelper.getEvaluator(table));
	},
	
	setAutoSort : function(table, enabled) {
		table.data("sonienAutoSort", enabled);
		TableHelper.sort(table);
	},
	
	isAutoSort : function(table) {
		return table.data("sonienAutoSort");
	},
	
	find : function(table, key) {
		var index = TableHelper.findIndex(table, key); 
		if(index < 0) {
			return null;
		}
		else {
			return WidgetHelper.getData(table)[index][1];
		}
	},
	
	findIndex : function(table, key) {
		return Sonien.binarySearch(WidgetHelper.getData(table), key, WidgetHelper.getEvaluator(table));
	},
	
	append : function(table, data, index) {
		var row = RowHelper.create(table, data)
		var children = $("tbody", table).children();
		
		if(index == null || index >= children.length) {
			$("tbody", table).append(row);
		}
		else {
			$(children[index]).before(row);
		}
		
		WidgetHelper.getData(table).push([data, row]);
		if(TableHelper.isAutoSort(table)) {
			TableHelper.sort(table);
		}
	},
	
	remove : function(table, key) {
		var records = WidgetHelper.getData(table);
		var index = TableHelper.findIndex(table, key);
		if(index >= 0) {
			records[index][1].remove();
			records.splice(index, 1);
		}
	},
	
	removeRow : function(table, row) {
		var evaluator 	= WidgetHelper.templator(table);
		var data 		= WidgetHelper.getData(row);
		TableHelper.remove(table, evaluator(data));
	},
	
	empty : function(table) {
		WidgetHelper.setData(table, []);
		$("tbody", table).empty();
	},
	
	setCallbackCreateRow : function(table, cb) {
		table.data("sonienCbCreateRow", cb);
		return table;
	},
	
	getCallbackCreateRow : function(table) {
		return table.data("sonienCbCreateRow"); 
	},
};

var RowHelper = {
	create : function(table, data) {
		var templator = table.data("sonienTemplate");
		var row = templator.apply(table, data);
		WidgetHelper.setData(row, data);
		
		var cbCreateRow = TableHelper.getCallbackCreateRow(table);
		if(cbCreateRow) {
			cbCreateRow(row, data, table);
		}
		return row;
	},
};

/* Table Widget helper */
(function($){
	$.fn.tableHelper = function() {
		switch(arguments[0]) {
		case "create" :
			TableHelper.create(this, arguments[1]);
			break;
		case "evaluator" :
			if(arguments.length == 1) {
				return WidgetHelper.getEvaluator(this);
			}
			else {
				WidgetHelper.setEvaluator(this, arguments[1]);
			}
			break;
		case "sort" :
			TableHelper.sort(this);
			break;
		case "auto-sort" :
			TableHelper.setAutoSort(this, arguments[1]);
			break;
		case "append" :
			TableHelper.append(this, arguments[1], arguments[2]);
			break;
		case "remove" :
			TableHelper.remove(this, arguments[1]);
			break;
		case "remove-row" :
			TableHelper.removeRow(this, arguments[1]);
			break;
		case "find" :
			return TableHelper.find(this, arguments[1]);
		case "find-index" :
			return TableHelper.findIndex(this, arguments[1]);
		case "empty" :
		case "remove-all" :
			TableHelper.empty(this);
			return this;
		case "callback" :
			switch(arguments[1]) {
			case "create" :
				if(arguments.length == 2) {
					return TableHelper.getCallbackCreateRow(this);
				}
				else {
					TableHelper.setCallbackCreateRow(this, arguments[2]);
				}
				break;
			}
		}
		
		return this;
	};
})(jQuery);

/* Tree Widget helper */
(function($){
	$.fn.treeHelper = function() {
		switch(arguments[0]) {
		case "create" :
			TreeHelper.create(this, arguments[1]);
			break;
		case "evaluator" :
			if(arguments.length == 1) {
				return WidgetHelper.getEvaluator(this);
			}
			else {
				WidgetHelper.setEvaluator(this, arguments[1]);
			}
			break;	
		case "sort" :
			TreeHelper.sort(this);
			break;
		case "callback" :
			switch(arguments[1]) {
			case "add" :
				if(arguments.length == 2) {
					return TreeHelper.getCallbackAddNode(this);
				}
				else {
					TreeHelper.setCallbackAddNode(this, arguments[2]);
				}
				break;
			case "remove" :
				if(arguments.length == 2) {
					return TreeHelper.getCallbackRemoveNode(this);
				}
				else {
					TreeHelper.setCallbackRemoveNode(this, arguments[2]);
				}
				break;
			case "create" :
				if(arguments.length == 2) {
					return TreeHelper.getCallbackCreateNode(this);
				}
				else {
					TreeHelper.setCallbackCreateNode(this, arguments[2]);
				}
				break;
			case "attach" :
				if(arguments.length == 2) {
					return TreeHelper.getCallbackAttachNode(this);
				}
				else {
					TreeHelper.setCallbackAttachNode(this, arguments[2]);
				}
				break;
			case "detach" :
				if(arguments.length == 2) {
					return TreeHelper.getCallbackDetachNode(this);
				}
				else {
					TreeHelper.setCallbackDetachNode(this, arguments[2]);
				}
				break;
			}
			break;
		case "toggling" :
			if(arguments.length == 1) {
				return TreeHelper.isToggling(this);
			}
			else {
				TreeHelper.setToggling(this, arguments[1]);
			}
			break;
		case "find" :
			return TreeHelper.findNode(this, arguments[1]);
		case "remove" :
			TreeHelper.removeNode(this, arguments[1]);
			break;
		case "addRoot" :
			return TreeHelper.addRoot(this, arguments[1]);
		}
		
		return this;
	};
})(jQuery);

/* Node Widget helper */
(function($){
	$.fn.nodeHelper = function() {
		switch(arguments[0]) {
		// Node 는 Tree 에 의해서만 생성 됨.
		// case "create" :
		// TableHelper.create(this, arguments[1]);
		// break;
				
		// Default Evaluator 는 Tree 의 것을 상속 받으며 변경 가능함.
		case "evaluator" :
			if(arguments.length == 1) {
				return WidgetHelper.getEvaluator(this);
			}
			else {
				WidgetHelper.setEvaluator(this, arguments[1]);
			}
			break;
		case "getDepth" :
			return NodeHelper.getDepth(this);
		case "addChild" :
			return NodeHelper.addChild(this, arguments[1]);
		case "toggle" :
			return NodeHelper.toggle(this);
		case "isCollapsed" :
			return NodeHelper.isCollapsed(this);
		case "childrenContainer" :
			return NodeHelper.childrenContainer(this);
		case "children" :
			return NodeHelper.children(this);
		case "hasChild" :
			return NodeHelper.hasChild(this);
		case "parent" :
			return NodeHelper.parent(this);
		case "isRoot" :
			return NodeHelper.isRoot(this);
		case "attachTo" :
			NodeHelper._detach(this);
			NodeHelper._attach(arguments[1], this);
			
			break;
		case "expand" :
			if(arguments.length == 1) {
				NodeHelper.expand(this, false);
			}
			else {
				NodeHelper.expand(this, arguments[1]);
			}
			break;
		}
		
		return this;
	};
})(jQuery);