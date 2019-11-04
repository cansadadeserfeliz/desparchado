$(function () {
  $('.datetimeinput').datetimepicker({
    locale: 'es',
    allowInputToggle: true,
    focusOnShow: true,
    icons: {
        time: 'fas fa-clock',
        date: 'fas fa-calendar',
        up: 'fas fa-arrow-up',
        down: 'fas fa-arrow-down',
        previous: 'fas fa-chevron-left',
        next: 'fas fa-chevron-right',
        today: 'fas fa-calendar-check',
        clear: 'fas fa-trash',
        close: 'fas fa-window-close'
    },
    tooltips: {
      today: 'Go to today',
      clear: 'Clear selection',
      close: 'Cerrar',
      selectMonth: 'Seleccionar el mes',
      prevMonth: 'Previous Month',
      nextMonth: 'Next Month',
      selectYear: 'Select Year',
      selectDate: 'Seleccionar la fecha',
      prevYear: 'Previous Year',
      nextYear: 'Next Year',
      selectDecade: 'Select Decade',
      prevDecade: 'Previous Decade',
      nextDecade: 'Next Decade',
      prevCentury: 'Previous Century',
      nextCentury: 'Next Century',
      incrementHour: 'Incrementar la hora',
      pickHour: 'Seleccionar la hora',
      decrementHour:'Disminuir la hora',
      incrementMinute: 'Incrementar minutos',
      pickMinute: 'Pick Minute',
      decrementMinute:'Disminuir minutos',
      incrementSecond: 'Increment Second',
      pickSecond: 'Seleccionar segundos',
      decrementSecond:'Decrement Second'
    },
    buttons: {
      showToday: false,
      showClear: false,
      showClose: true
    },
    keepOpen: false,
    widgetPositioning: {
      horizontal: 'auto',
      vertical: 'top'
    },
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
