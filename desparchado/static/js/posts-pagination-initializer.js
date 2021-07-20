$(function() {
$('#history_post_pagination').infiniteScroll({
  path: getPenPath,
  append: '.post',
  status: '.page-load-status',
  prefill: true,
  history: false,
});

function getPenPath() {
  let pageNumber = this.loadCount + 1;
  return `/historia/posts/?page=${pageNumber}`;
}

});



