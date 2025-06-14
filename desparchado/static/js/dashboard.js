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
      let event_time = info.el.querySelectorAll('.fc-event-time')[0]
      if (info.event.extendedProps.imageUrl && event_time) {
        let image_el = document.createElement("img");
        image_el.setAttribute('src', info.event.extendedProps.imageUrl);

        let div_el = document.createElement("div");
        div_el.setAttribute('class', 'fc-image');
        div_el.appendChild(image_el)

        event_time.before(div_el);
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
