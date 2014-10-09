/* 소년 스튜디오 라이브러리 */
var Sonien = {
	// Copyright 2009 Nicholas C. Zakas. All rights reserved.
	// MIT-Licensed, see source file
	binarySearch : function(array, value, evaluator) {
		if (array.length == 0)
			return -1;

		evaluator = evaluator || function(value) { return value };

		var startIndex = 0, stopIndex = array.length - 1, middle = Math
				.floor((stopIndex + startIndex) / 2), middleValue = evaluator(array[middle]);

		while (middleValue != value && startIndex < stopIndex) {
			// adjust search area
			if (value < middleValue) {
				if((stopIndex = middle - 1) < 0) {
					stopIndex = 0;
				};
				
			} else if (value > middleValue) {
				if((startIndex = middle + 1) >= array.length) {
					startIndex = array.length - 1;
				};
			}

			// recalculate middle
			middle = Math.floor((stopIndex + startIndex) / 2);
			middleValue = evaluator(array[middle]);
		}
		return (middleValue != value) ? -1 : middle;
	},

	deduplicate : function(array, keyIndexs) {
		var uniqueArray = [];
		array.sort();
		var lastRecord = null;
		for (var i = 0; i < array.length; i++) {
			if (lastRecord == array[i])
				continue;
			uniqueArray.push(array[i]);
			lastRecord = array[i];
		}

		return uniqueArray;
	},

	trimArray : function(src, keyIndexs) {
		var array = [];
		for (var i = 0; i < src.length; i++) {
			if (src[i] == "")
				continue;

			array.push(src[i]);
		}

		return array;
	},

	getFileSizeString : function(value) {
		var unit = [ "B", "K", "M", "G", "T" ];
		var unitIndex = 0;
		for (var i = 1; value >= 1024 && i < unit.length; i++) {
			value = value / 1024;
			unitIndex = i;
		}

		return "" + value.toFixed(1) + unit[unitIndex]// String.format("%.1f
		// %c", value,
		// unit[unitIndex]);
	},
	
	download : function(url, data, method){
	    // url과 data를 입력받음
	    if( url && data ){ 
	        // data 는  string 또는 array/object 를 파라미터로 받는다.
	        data = typeof data == 'string' ? data : jQuery.param(data);
	        // 파라미터를 form의  input으로 만든다.
	        var inputs = '';
	        jQuery.each(data.split('&'), function(){ 
	            var pair = this.split('=');
	            inputs+='<input type="hidden" name="'+ pair[0] +'" value="'+ pair[1] +'" />'; 
	        });
	        // request를 보낸다.
	        jQuery('<form action="'+ url +'" method="'+ (method||'post') +'" data-ajax="false">'+inputs+'</form>')
	        .appendTo('body').submit().remove();
	    }
	}
}

/**
 * Enhanced QuickSort - original by Paul Lewis
 * 
 * This is for making QuickSort of List or Dictionary. Additional 'evaluator'
 * parameter is providing extraction of key value of the element. 'evaluator'
 * parameter should be a function which is implemented by user. Or if it is
 * null, than it will work as normal QuickSort.
 * 
 * Tests with:
 * 
 * var array = []; for(var i = 0; i < 20; i++) { array.push({ key : i, value :
 * Math.round(Math.random() * 100)}); }
 * 
 * Quicksort.sort(array, function(value) { return value["value"] });
 * 
 * 
 * Enhanced by SonienTagei
 * 
 *  * Original Copyright
 * 
 * An implementation for Quicksort. Doesn't perform as well as the native
 * Array.sort and also runs the risk of a stack overflow
 * 
 * Tests with:
 * 
 * var array = []; for(var i = 0; i < 20; i++) {
 * array.push(Math.round(Math.random() * 100)); }
 * 
 * Quicksort.sort(array);
 * 
 * @author Paul Lewis
 * 
 */
var Quicksort = (function() {

	/**
	 * Swaps two values in the heap
	 * 
	 * @param {int}
	 *            indexA Index of the first item to be swapped
	 * @param {int}
	 *            indexB Index of the second item to be swapped
	 */
	function swap(array, indexA, indexB) {
		var temp = array[indexA];
		array[indexA] = array[indexB];
		array[indexB] = temp;
	}

	/**
	 * Partitions the (sub)array into values less than and greater than the
	 * pivot value
	 * 
	 * @param {Array}
	 *            array The target array
	 * @param {int}
	 *            pivot The index of the pivot
	 * @param {int}
	 *            left The index of the leftmost element
	 * @param {int}
	 *            left The index of the rightmost element
	 */
	function partition(array, pivot, left, right, evaluator) {

		var storeIndex = left, pivotValue = evaluator(array[pivot]);

		// put the pivot on the right
		swap(array, pivot, right);

		// go through the rest
		for (var v = left; v < right; v++) {

			// if the value is less than the pivot's
			// value put it to the left of the pivot
			// point and move the pivot point along one
			if (evaluator(array[v]) < pivotValue) {
				swap(array, v, storeIndex);
				storeIndex++;
			}
		}

		// finally put the pivot in the correct place
		swap(array, right, storeIndex);

		return storeIndex;
	}

	/**
	 * Sorts the (sub-)array
	 * 
	 * @param {Array}
	 *            array The target array
	 * @param {int}
	 *            left The index of the leftmost element, defaults 0
	 * @param {int}
	 *            left The index of the rightmost element, defaults
	 *            array.length-1
	 */
	function sort(array, evaluator, left, right) {
		evaluator = evaluator || function(value) {
			return value
		};

		var pivot = null;

		if (typeof left !== 'number') {
			left = 0;
		}

		if (typeof right !== 'number') {
			right = array.length - 1;
		}

		// effectively set our base
		// case here. When left == right
		// we'll stop
		if (left < right) {

			// pick a pivot between left and right
			// and update it once we've partitioned
			// the array to values < than or > than
			// the pivot value
			pivot = left + Math.ceil((right - left) * 0.5);
			newPivot = partition(array, pivot, left, right, evaluator);

			// recursively sort to the left and right
			sort(array, evaluator, left, newPivot - 1);
			sort(array, evaluator, newPivot + 1, right);
		}

	}

	return {
		sort : sort
	};

})();
