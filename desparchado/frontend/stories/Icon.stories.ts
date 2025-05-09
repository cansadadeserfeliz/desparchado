import Icon from '@presentational_components/foundation/icon/Icon.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/Icon',
  component: Icon,
  tags: ['autodocs'],
  argTypes: {
    id: {
      control: 'select',
      options: ['user', 'more-vertical', 'instagram', 'xsocial', 'facebook'],
    },
    size: {
      control: 'select',
      options: ['regular', 'small', 'unset'],
    },
  },
  args: {
    id: 'user',
  },
} satisfies Meta<typeof Icon>;

export default meta;

type Story = StoryObj<typeof meta>;

export const SmallIcon: Story = {
  args: {
    size: 'small',
    id: 'user',
  },
};

export const User: Story = {
  args: {
    id: 'user',
  },
};

export const MoreVertical: Story = {
  args: {
    id: 'more-vertical',
  },
};

export const Instagram: Story = {
  args: {
    id: 'instagram',
  },
};

export const Facebook: Story = {
  args: {
    id: 'facebook',
  },
};

export const XSocial: Story = {
  args: {
    id: 'xsocial',
  },
};
