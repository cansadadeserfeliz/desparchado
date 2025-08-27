import { getEventList } from './api/events';
import { Component, createApp, defineComponent, h, PropType } from 'vue';
import { IEvent } from './api/interfaces';
import { EventCardProps } from '@presentational_components/components/event-card/EventCard.vue';
import EventCard from '@presentational_components/components/event-card/EventCard.vue';

const EventsListApp = defineComponent({
  name: 'EventsListApp',
  props: {
    events: { type: Array as PropType<EventCardProps[]>, required: true },
    card: { type: Object as PropType<Component>, default: () => EventCard },
  },
  setup(props) {
    return () =>
      h(
        'div',
        { class: 'events-list' },
        props.events.map((e, i) => h(props.card, { ...e, key: e.title ?? i })),
      );
  },
});

/**
 * Map an IEvent to EventCardProps for the EventCard component
 * @param event The event data from the API
 * @returns Props for the EventCard component
 */
function mapEventToCardProps(events: IEvent[]): EventCardProps[] {
  return events.map((event) => ({
    tag: 'div',
    customClass: 'events-list__card',
    location: event.place.name,
    title: event.title,
    description: event.description,
    day: event.formatted_day,
    time: event.formatted_hour,
    imageUrl: event.image_url,
  }));
}

// --- The class the DOM bootstraps ---
export class EventContainer {
  private readonly el: HTMLElement;

  constructor(el: HTMLElement) {
    this.el = el;
    const url = el.dataset.url;
    if (!url) {
      throw new Error('EventContainer: data-url not found on element');
    }

    this.init(url);
  }

  protected init(url: string): void {
    getEventList(url)
      .then((data) => {
        this.createContainerVueElement(mapEventToCardProps(data.results));
      })
      .catch((err) => {
        console.error('Failed to load events:', err);
      });
    console.log(url);
  }

  private createContainerVueElement(events: EventCardProps[]): void {
    createApp(EventsListApp, { events }).mount(this.el);
  }
}
