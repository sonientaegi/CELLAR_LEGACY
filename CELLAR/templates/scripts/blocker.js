/*
	*** Notice! ***
	
	Blocker should be acquired or released by main thread. 
	Neither Blocker nor JavaScript doesn't support multi-thread, blocker should be only called by main thread of browser.
	Please remeber Worker is not allowed to access Blocker.
*/
var Blocker = {
	_counter : 0,
	
	acquire : function(text) {
		text = text || "on progress ...";
		
		if(Blocker._counter == 0) {
			$("#blocker").show();
			$.mobile.loading("show", {
				text : text,
				textVisible : true
			});
		}
		Blocker._counter = Blocker._counter + 1; 
	},
	
	release : function() {
		Blocker._counter = Blocker._counter - 1;
		if(Blocker._counter <= 0) {
			Blocker._counter = 0
			$("#blocker").hide();
			$.mobile.loading("hide");
		}
	},
	
	reset : function() {
		Blocker._counter = 0;
		$("#blocker").hide();
		$.mobile.loading("hide");
	}
};