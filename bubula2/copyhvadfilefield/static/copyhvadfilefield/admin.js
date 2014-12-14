"use strict";

django.jQuery(document).ready(function($) {
	var pEmptyForm = /^[a-z]+-empty$/,
		pModelKey = /^[a-z]+/,
		pLangDeleteUrl = /^\.\/delete-translation\/([a-z]+)\/$/;
	
	function get_site_param(param) {
		var re = new RegExp('\\??(?:[^=]+=[^&]*&)*'+param+'=([^&]*)', 'g'),
			val = void(0);
		window.location.search.replace(re, function(s, v) {
			val = v;
		});
		return val;
	}
	
	$('.nani-language-tabs ~ div input[type="file"]').each(function() {
		var inputField = $(this),
			buttonCnt = inputField.parent(),
			objDOMId = inputField.parents('fieldset').parent().attr('id'),
			objId = $('#id_'+objDOMId+'-id').val();
		if ( objDOMId.match(pEmptyForm) || !objId ) {
			return;
		}
		
		$('<input type="button" style="margin-left:0.5em;" value="Copy from other language" title="This will save the object!"/>').
			appendTo(buttonCnt).
			click(function(e) {
				e.preventDefault();
				var args,
					curLang = get_site_param('language'),
					modelKey = objDOMId.match(pModelKey)[0],
					model = CHFF_MODELS[modelKey], // must be defined by other included script
					inputName = inputField.attr('name'),
					field = inputName.match( new RegExp(objDOMId+'-([a-zA-Z0-9_]+)$') )[1];
				if (!curLang) {
					curLang = $('html').attr('lang');
				}
				args = {
					'curLang': curLang,
					'modelStr': model,
					'field': field,
					'objId': objId
				}
				Dajaxice.copyhvadfilefield.copy_from_other(
					function(data) {
						if (!data['success']) {
							alert(data['errorMsg']);
							return;
						}
						currentLink = inputField.parent().children('a');
						if (currentLink.length) {
							currentLink.
								attr('href', data['newUrl']).
								text(data['newFile']);
						} else {
							buttonCnt.append('<span style="padding-left:1em;">Set to "'+data['newFile']+'"</span>');
						}
					},
					args
				);
				return false;
			});;
	});			
});
