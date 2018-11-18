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

  function show_suggestion(suggestion_message) {
    $('.show-suggestions').after(
      '<span class="suggestions-feedback text-warning">' +
      suggestion_message + '</span>'
    );
  }

  function hide_suggestions(elem) {
    $('.suggestions-feedback').remove();
  }

  $('.show-suggestions').on('keydown', function() {
    var suggestion_elem = $(this);
    console.log(suggestion_elem);
    console.log(suggestion_elem.data('suggestions-url'));
    console.log(suggestion_elem.val());
    $.get(suggestion_elem.data('suggestions-url'), {'query': suggestion_elem.val()}, function(data) {
      console.log(data.suggestion);
      hide_suggestions();
      if (data.suggestion) {
        show_suggestion(data.suggestion);
      } else {
        hide_suggestions();
      }

    });
  });

});
