document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById('social_posts_calendar');

  const calendar = new FullCalendar.Calendar(calendarEl, {
    timeZone: 'America/Bogota',
    initialView: 'timeGridWeek',
    firstDay: 1,
    headerToolbar: {
      left: 'prev,next today refreshButton',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    customButtons: {
      refreshButton: {
        text: 'refresh',
        click: function () {
          calendar.refetchEvents();
        }
      }
    },
    buttonText: {
      today: 'today',
      month: 'month',
      week: 'week',
      day: 'day'
    },
    eventSources: [
      {
        url: '/dashboard/social-posts/source'
      }
    ],
    eventDidMount: function(info) {
      if (info.event.extendedProps.imageUrl) {
        const img = document.createElement('img');
        img.src = info.event.extendedProps.imageUrl;
        img.width = 70;
        info.el.querySelector('.fc-event-title').appendChild(document.createElement('br'));
        info.el.querySelector('.fc-event-title').appendChild(img);
      }
    },
    slotLabelFormat: {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }
  });

  calendar.render();
});
