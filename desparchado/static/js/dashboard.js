$(function() {

  // page is now ready, initialize the calendar...

  $('#social_posts_calendar').fullCalendar({
    header: {
      left  : 'prev,next today',
      center: 'title',
      right : 'month,agendaWeek,agendaDay'
    },
    buttonText: {
      today: 'today',
      month: 'month',
      week : 'week',
      day  : 'day'
    },
    defaultView: 'month',
    firstDay: 1,
    timeFormat: 'hh:mm',
    eventSources: [
      '/dashboard/social-posts/source'
    ]
  })

});
