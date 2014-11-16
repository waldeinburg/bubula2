"use strict";

/* CopyHvadFileField models */
var CHFF_MODELS = {
	'normalcomic': 'NormalComic'
};

/* Only show currently selected type */
django.jQuery(document).ready(function($) {
	var $types = $();

	function changeType() {
		var type = $('#id_type').val().toLowerCase();
		$types.addClass('hidden');
		$('#'+type+'-group').removeClass('hidden');
	}
	// FIXME: if making an error in one type, changing type and saving, the errors are invisible until switching type back
	if ( $('#id_type').length ) {
		var typeIds = [];
		
		/* only match inline-groups that belong to a comic type */
		$('#id_type option').each(function(k, e) {
			typeIds.push( $(e).attr('value').toLowerCase() );
		});
		$('.inline-group').each(function(k, e) {
			var $e = $(e);
			if ( typeIds.indexOf( $e.attr('id').match(/^(.+?)-group$/)[1] ) != -1  ) {
				$types = $types.add($e);
			}
		});

		$('#id_type').change(changeType);
		changeType();
	}	
});
