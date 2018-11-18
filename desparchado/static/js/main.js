$(function () {
  $('.datetimeinput').datetimepicker({
    locale: 'es',
    format: 'DD/MM/YYYY HH:mm'
  });

  // Mark sub-header menu element as active
  $( ".users-sub-header a" ).each(function(index) {
    var current_path = $(this).attr('href');
    if (current_path == window.location.pathname || window.location.pathname.lastIndexOf(current_path, 0) === 0) {
      $(this).parents('li').addClass('active');
    }
  });
});
