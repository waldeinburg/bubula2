jQuery(document).ready(function($) {
	$('#paypal form').submit(function(e) {
		var errorMsg = {
				'da': 'Ugyldigt beløb!',
				'en': 'Invalid amount!'
			},
			p = /^\s*\d+(\.\d{1,2})?\s*$/,
			amountInput = $('#paypal form input[name="amount"]'),
			val = amountInput.val();
		val = val.replace(',', '.');
		if ( !val.match(p) ) {
			alert(errorMsg[global.lang]);
			e.preventDefault();
			return false;			
		}
		amountInput.val(val); // if we replaced comma with dot
		return true;
	});
});