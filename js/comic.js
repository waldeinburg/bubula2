(function($) {
    /* Create date menu. 
     * Don't wait for this until document.onready. When script is placed at the bottom, the DOM is ready now.
     */
    $('#comic-date').
        wrapInner('<span/>').
        dropdown({
            'click': function(){ return false; }
        }).
        one('click', function(e) {
            e.preventDefault();
            var elem = $(this),
                content = elem.dropdown('content'),
                loading = $('<div/>').
                text('Loading comic list …').
                appendTo(content);
            $.ajax('/'+comic.lang+'/comics.json', {
                success: function(data) {
                    console.log(data);
                    loading.remove();
                    var list = $('<ul/>').appendTo(content);
                    $.each(data.comics, function() {
                        var item = $('<li/>').appendTo(list),
                            itemA = $('<a/>').
                                attr('href', comic.comicsUrlPath+this.id.toString()+'/').
                                appendTo(item);
                        if (comic.id == this.id) {
                            item.addClass('current');
                            //TODO: scroll to current
                        }
                        $('<span/>').
                            css('text-style', 'italic').
                            text(this.date).
                            appendTo(itemA);
                        $('<span/>').
                            text(this.title).
                            appendTo(itemA);
                    });
                    elem.dropdown('hide');
                    content.css('overflow-y', 'scroll');
                    setTimeout(function() {
                        elem.
                            dropdown('option', {
                                'toggleEffect': 'slide',
                                'toggleEffectOptions': {'direction':'up'}
                            }).
                            dropdown('show');
                    }, 100);
                }
            });
            return false;
        });
    
    
    /*
     * Oh No Robot loader
     * Oh No Robot has a tendency to load slow. Insert after everything else is loaded.
     * Inline Script is not good enough because ONR-lack will affect js triggered by the ready event.
     * Wait till everything else is loaded.
     */
    $(document).ready(function($) {
        // http://api.jquery.com/jQuery.getScript/
        // should we override the cache setting temporarily?
        $.getScript('http://www.ohnorobot.com/js/2033.js', function() {
            orgW = document.write;
            document.write = function(s) { $('#ohnorobot').append(s); };
            transcribe('apqYa6imImgok2033', comic.url, comic.title);
            document.write = orgW;
        });
    });
})(jQuery);
