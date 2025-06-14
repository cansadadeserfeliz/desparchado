document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById('social_posts_calendar');

  const calendar = new FullCalendar.Calendar(calendarEl, {
    timeZone: 'America/Bogota',
    initialView: 'timeGridWeek',
    firstDay: 1,
    headerToolbar: {
      left: 'prev,next today refreshButton',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
    },
    customButtons: {
      refreshButton: {
        text: 'refresh',
        click: function () {
          calendar.refetchEvents();
        }
      }
    },
    eventSources: [
      {
        url: '/dashboard/social-posts/source'
      }
    ],
    eventDidMount: function(info) {
      const eventTimeEl = info.el.querySelector('.fc-event-time');
      if (info.event.extendedProps.imageUrl && eventTimeEl) {
        const img = document.createElement('img');
        img.src = info.event.extendedProps.imageUrl;

        const container = document.createElement('div');
        container.className = 'fc-image';
        container.appendChild(img)

        eventTimeEl.before(container);
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
