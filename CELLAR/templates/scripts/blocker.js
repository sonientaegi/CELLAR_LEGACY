/*
	*** Notice! ***
	
	Blocker should be acquired or released by main thread. 
	Neither Blocker nor JavaScript doesn't support multi-thread, blocker should be only called by main thread of browser.
	Please remeber Worker is not allowed to access Blocker.
*/
var Blocker = {
	_window		: null,
	_counter 	: 0,
	
	/**
	 * Initialize Blocker.
	 * 
	 * @param selector jQuery selector instance to do as a blocking window to prevent user input
	 */
	initialize 	: function(selector) {
		Blocker._window = selector;
	},
	
	/**
	 * Activate blocking window to prevent user input. Also display a loading dialog with text.
	 * Like semaphore, acquire increase counter.
	 * 
	 * @param text
	 */
	acquire : function(text) {
		text = text || "on progress ...";
		
		if(Blocker._counter == 0) {
			Blocker._window.show();
			$.mobile.loading("show", {
				text : text,
				textVisible : true
			});
		}
		Blocker._counter = Blocker._counter + 1; 
	},
	
	/**
	 * Like semaphore, release decrease counter. When counter getting 0, blocking window and dialog will be deactivated.
	 */
	release : function() {
		Blocker._counter = Blocker._counter - 1;
		if(Blocker._counter <= 0) {
			Blocker._counter = 0
			Blocker._window.hide();
			$.mobile.loading("hide");
		}
	},
	
	/**
	 * Reset deactivates blocking window any time, regardless of block counter.
	 * Block counter will be set 0.
	 */
	reset : function() {
		Blocker._counter = 0;
		Blocker._window.hide();
		$.mobile.loading("hide");
	}
};