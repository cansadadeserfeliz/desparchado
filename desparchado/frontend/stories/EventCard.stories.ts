import EventCard from '@presentational_components/components/event-card/EventCard.vue';
import type { Decorator, Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/EventCard',
  component: EventCard,
  tags: ['autodocs'],
  argTypes: {
    tag: {
      control: 'select',
      options: ['div', 'li', 'section', 'article'],
    },
  },
  args: {
    tag: 'div',
  },
} satisfies Meta<typeof EventCard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const NormalCard: Story = {
  args: {
    tag: 'div',
    location: 'Biblioteca Luis Ángel Aranjo',
    description:
      'A cumplirse 100 años de la primera publicación de La Vorágine, Margarita Serje nos muestra los mapas que el autor incluyó y que fueron omitidos en ediciones posteriores. Asimismo, la edición cosmográfica de este clásico.',
    title: 'No estamos solos la paz también se hace con animales',
    day: '17 Jun',
    time: '22:00',
  },
  decorators: [
    (() => ({
      template: `
      <div style="height: 500px;">
        <story />
      </div>
    `,
    })) as Decorator,
  ],
};
