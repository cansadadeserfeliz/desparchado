let history_post_wrapper = document.getElementById('history_post_pagination');
if (history_post_wrapper) {
    let infScroll = new InfiniteScroll(history_post_wrapper, {
        path: history_post_wrapper.dataset.infiniteScrollPath + '?page={{#}}',
        status: '.js-page-load-status',
        append: false,
        responseBody: 'json',
        prefill: true,
        history: false,
    });

    infScroll.on('load', function(body) {
        // compile body data into HTML
        var itemsHTML = body.posts.join('');
        // convert HTML string into elements
        let elems = stringToHTML(itemsHTML)
        infScroll.appendItems(elems.children);
    });

    // load initial page
    infScroll.loadNextPage();
}

/**
 * Convert a template string into HTML DOM nodes
 * @param  {String} str The template string
 * @return {Node}       The template HTML
 */
var stringToHTML = function (str) {
    var dom = document.createElement('div');
    dom.innerHTML = str;
    return dom;
};
