$(function() {

  // page is now ready, initialize the calendar...

  $('#social_posts_calendar').fullCalendar({
    customButtons: {
      refreshButton: {
        text: 'refresh',
        click: function() {
          $('#social_posts_calendar').fullCalendar('refetchEvents')
        }
      }
    },
    header: {
      left  : 'prev,next today refreshButton',
      center: 'title',
      right : 'month,agendaWeek,agendaDay'
    },
    buttonText: {
      today: 'today',
      month: 'month',
      week : 'week',
      day  : 'day'
    },
    defaultView: 'agendaWeek',
    firstDay: 1,
    timeFormat: 'hh:mm',
    eventRender: function(event, eventElement) {
      if (event.imageUrl) {
        eventElement.find("div.fc-content").append("<br><img src='" + event.imageUrl +"' width='70'>");
      }
    },
    eventSources: [
      '/dashboard/social-posts/source'
    ]
  })

});
