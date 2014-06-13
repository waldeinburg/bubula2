"use strict";

/* script is loaded at bottom of page, so I keep the execution at ready event only because
 * these actions are not needed before everything else is loaded
 */ 
jQuery(document).ready(function($) {
	/* create mailto-links.
	 * The link should be:
	 * This technique means:
	 * - somewhat paranoid spam-bot protection (TODO: encryption)
	 * - we don't need to define any functions in head to avoid javascript errors when
	 *   clicking a link - the email-address is nothing but a span until now.
	 *   I don't wan't mailto-links with "contact" text anyway; email-addresses should be
	 *   copy-able.
	 */
	
	$('.postbud').each(function() {
		var span = $(this),
			user = span.children('.p-u').text(),
			hostSub = span.children('.p-s').text(),
			hostTop = span.children('.p-t').text(),
			title = span.attr('title'),
			link = $('<a/>').
				insertBefore(span).
				append( span.contents() );

		span.remove(); // remove the now empty span

		link.
			attr('href', '#').
			click(function(e) {
				e.preventDefault();
				location.href = 'm'+'ailto:'+user+'@'+hostSub+'.'+hostTop;
				return false;
			});

		if (title) {
			link.attr('title', title);
		}			
	});
	
	/* replace antispam-classes. :before cannot be copy-pasted but functions as noscript */
	$('span.transmogrifyAffenschwanz').
		removeClass('transmogrifyAffenschwanz').
		text('@');
	$('span.transmogrifyDaDot').
		removeClass('transmogrifyDaDot').
		text('.');
});