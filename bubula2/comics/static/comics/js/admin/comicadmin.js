CHFF_MODELS = {
	'normalcomic': 'NormalComic'
};

django.jQuery(document).ready(function($) {
	// TODO: if making an error in one type, changing type and saving, the errors are invisible until switching type back
	function changeType() {
		$('.inline-group').addClass('hidden');
		type = $('#id_type').val().toLowerCase();
		$('#'+type+'-group').removeClass('hidden');
	}
	
	if ( $('#id_type').length ) {
		$('#id_type').change(function() {
			changeType();
		});
		changeType();
	}	
});