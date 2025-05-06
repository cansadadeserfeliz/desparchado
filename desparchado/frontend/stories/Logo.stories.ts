import Logo from '@presentational_components/atoms/logo/Logo.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/Logo',
  component: Logo,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['isotype', 'imagotype', 'isologo'],
    },
  },
  args: {
    type: 'imagotype',
  },
} satisfies Meta<typeof Logo>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Imagotype: Story = {
  args: {
    type: 'imagotype',
  },
};

export const Isotype: Story = {
  args: {
    type: 'isotype',
  },
};

export const Isologo: Story = {
  args: {
    type: 'isologo',
  },
};
