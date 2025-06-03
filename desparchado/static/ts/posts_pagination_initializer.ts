// Ensure InfiniteScroll is properly typed, e.g., via @types/infinite-scroll or custom declaration
declare class InfiniteScroll {
    constructor(element: Element, options: {
        path: string;
        status: string;
        append: boolean;
        responseBody: 'json';
        prefill: boolean;
        history: boolean;
    });

    on(event: 'load', callback: (body: { posts: string[] }) => void): void;
    appendItems(elems: HTMLCollection): void;
    loadNextPage(): void;
}

const historyPostWrapper = document.getElementById('history_post_pagination');
if (historyPostWrapper) {
    const pathBase = historyPostWrapper.dataset.infiniteScrollPath;
    if (!pathBase) {
        console.error('Missing data-infinite-scroll-path on element');
    } else {
        const infScroll = new InfiniteScroll(historyPostWrapper, {
            path: `${pathBase}?page={{#}}`,
            status: '.js-page-load-status',
            append: false,
            responseBody: 'json',
            prefill: true,
            history: false,
        });

        infScroll.on('load', (body: { posts: string[] }) => {
            const itemsHTML = body.posts.join('');
            const elems = stringToHTML(itemsHTML);
            infScroll.appendItems(elems.children);
        });

        // load initial page
        infScroll.loadNextPage();
    }
}

/**
 * Convert a template string into HTML DOM nodes
 * @param  str The template string
 * @return     The template HTML
 */
function stringToHTML(str: string): HTMLElement {
    const dom = document.createElement('div');
    dom.innerHTML = str;
    return dom;
}
