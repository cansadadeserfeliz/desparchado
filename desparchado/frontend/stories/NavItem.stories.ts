import NavItem from '@presentational_components/atoms/nav-item/NavItem.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/NavItem',
  component: NavItem,
  tags: ['autodocs'],
  argTypes: {},
  args: {
    active: false,
  },
} satisfies Meta<typeof NavItem>;

export default meta;

type Story = StoryObj<typeof meta>;

export const LinkItem: Story = {
  args: {
    label: 'Item',
    link: 'google.com',
  },
};

export const ActiveItem: Story = {
  args: {
    label: 'Item',
    link: 'google.com',
    active: true,
  },
};
