/*
The MIT License

Copyright (c) 2011 Daniel Lundsgaard Skovenborg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
 */

$.extend({
	is_def: function(v) {
		return (v !== void(0));
	},
	
	
	/**
	 * Inherit
	 * Almost copy from Google Closure
	 */
	inherits: function(childCtor, parentCtor) {
		/* use temporary object to copy prototype,
		 * else overridden method will change parent. */
		function tmpCtor() {};
		tmpCtor.prototype = parentCtor.prototype;
		childCtor.prototype = new tmpCtor();
		childCtor.prototype.constructor = childCtor;
		/* access to parent implementation of overridden functions
		 * Superclass functions cannot have access to properties,
		 * therefore superClass is not put in prototype.
		 */
		childCtor.superClass = parentCtor.prototype;
	},
	
	
	/**
	 * Abstract method
	 * Simply throws an error. Calling this in a method will make it abstract.
	 */
	abstract_method: function() {
		throw "Abstract method not implemented.";
	},
	
	
	/**
	 * Set options
	 * 
	 * @param self Object to set properties on
	 * @param options Map of options
	 * @param defaults (optional) Map of defaults
	 */
	set_options: function(self, options, /*optional*/ defaults) {
		var options = $.is_def(options) ? options : {}
		if ($.is_def(defaults)) {
			$.each(defaults, function(o, defVal) {
				self[o] = $.is_def(options[o]) ? options[o] : defVal;
			});
		} else {
			$.extend(self, options);
		}
	},
		
	
	/**
	 * Set arguments
	 * Like options, but for cases where there's no defaults.
	 * Shortcut to a list of this.foo = foo
	 * 
	 * @param self
	 * @param args Arguments
	 * @param keys Array of keys
	 */
	set_arguments: function(self, args, keys) {
		$.each(keys, function(i, k) {
			self[k] = args[i];
		});
	}
});