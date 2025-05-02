import FeaturedEventCard from '@presentational_components/components/featured-event-card/FeaturedEventCard.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/FeaturedEventCard',
  component: FeaturedEventCard,
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
} satisfies Meta<typeof FeaturedEventCard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const NormalCard: Story = {
  args: {
    tag: 'div',
    location: 'Biblioteca Luis Ángel Aranjo',
    title: 'No estamos solos la paz también se hace con animales',
    day: '17 Jun',
    time: '22:00',
  },
};
