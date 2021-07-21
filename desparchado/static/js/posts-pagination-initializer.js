let history_post_wrapper = document.getElementById('history_post_pagination');
let infScroll = new InfiniteScroll(history_post_wrapper, {
  path: history_post_wrapper.dataset.infiniteScrollPath + '?page={{#}}',
  append: '.post',
  status: '.page-load-status',
  prefill: true,
  history: false,
});
