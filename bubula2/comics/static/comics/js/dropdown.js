(function($){
	/**
	 * Creates a drop-down box
	 * .... or at least it should. TODO: implement beyond what is needed for this project
	 * Should be applied to an element with two children, title and drop-down content.
	 * Example:
	 * - a span with the the title (e.g. "select item")
	 * - a ul with items
	 */
	$.widget('ui_ext.dropdown', {
		options: {
			'toggleEffect': undefined,
			'toggleEffectOptions': undefined,
//			'scroll': true,
//			'width': 'auto',
//			'height': '10em', // irrelevant if scroll is false
//			'onDropdown': function(){ return true; },
			'onSelect': function(){ return true; },
//			'onScroll': function(){ return true; }
		},
		
		_value: null,
		
		_create: function() {
			var
				self = this,
				components = this.element.children(),
				title = components.first(),
				content = components.slice(1, 2);
			
			this.element.
				addClass('ui-dropdown').
				wrapInner('<dl/>').
				on('click', 'dd ul li', this, this._itemSelect);
			title.
				wrap('<dt/>').
				click(function() {
					self._content.toggle(self.options.toggleEffect, self.options.toggleEffectOptions);
					return true;
				});
			$(document).click(function(e) {
				var clicked = $(e.target);
				if ( !clicked.hasClass('ui-dropdown') && !clicked.parents().hasClass('ui-dropdown') ) {
					if ( self._content.css('display') != 'none' ) {
						self._content.hide(self.options.toggleEffect, self.options.toggleEffectOptions);
					}
				}
			});
			if (content.length) {
				content.wrap('<dd/>');
			} else {
				this.element.children('dl').append('<dd/>');
			}
			this._title = title.parent();
			this._content = this.element.find('dd');
			this._content.hide();
		},
		
		content: function() {
			return this._content;
		},
		
		value: function() {
			return this._value;
		},
		
		_itemSelect: function(event) {
			that = event.data;
			if ( that.options.onSelect() ) {
				that._value = event;
			}
		},
		
		get_options: function() {
			return this.options;
		},
		
		show: function() {
			this._content.show(this.options.toggleEffect, this.options.toggleEffectOptions);
		},
		
		hide: function() {
			this._content.hide(this.options.toggleEffect, this.options.toggleEffectOptions);
		},		
	});
})(jQuery);