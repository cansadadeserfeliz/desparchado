import Button from '@presentational_components/atoms/button/Button.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['primary', 'secondary', 'tertiary'],
    },
    condensed: {
      control: 'boolean',
    },
    link: {
      control: 'text',
      description: 'Link to transform button into anchor if provided',
    },
  },
  args: {
    type: 'primary',
    condensed: false,
  },
} satisfies Meta<typeof Button>;

export default meta;

type Story = StoryObj<typeof meta>;

export const CondensedButton: Story = {
  args: {
    type: 'primary',
    label: 'Leer más',
    condensed: true,
    link: 'google.com',
  },
};

export const PrimaryButton: Story = {
  args: {
    type: 'primary',
    label: 'Leer más',
  },
};

export const SecondaryButton: Story = {
  args: {
    type: 'secondary',
    label: 'Leer más',
  },
};

export const TertiaryButton: Story = {
  args: {
    type: 'tertiary',
    label: 'Leer más',
  },
};

export const LinkButton: Story = {
  args: {
    type: 'primary',
    label: 'Leer más',
    link: 'google.com',
  },
};
