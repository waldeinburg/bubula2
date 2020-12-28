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
    
    $('.random-comic').click(function() {
        var id = Math.floor(Math.random() * comic.latestId) + 1;
        window.location = comic.comicsUrlPath + id + '/';
    });
})(jQuery);
