import Button from '@presentational_components/atoms/button/Button.vue';
import Icon from '@presentational_components/foundation/icon/Icon.vue';
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
    padding: {
      control: 'select',
      options: ['condensed', 'balanced', 'regular'],
    },
    radius: {
      control: 'select',
      options: ['squared', 'soft', 'circular'],
    },
    link: {
      control: 'text',
      description: 'Link to transform button into anchor if provided',
    },
  },
} satisfies Meta<typeof Button>;

export default meta;

type Story = StoryObj<typeof meta>;

export const CondensedButton: Story = {
  args: {
    type: 'primary',
    label: 'Leer más',
    padding: 'condensed',
    link: 'google.com',
  },
};

export const BalancedButton: Story = {
  args: {
    type: 'primary',
    label: 'Leer más',
    padding: 'balanced',
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

export const OnlyIconButton: Story = {
  args: {
    type: 'primary',
    padding: 'balanced',
  },
  render: (args) => ({
    components: { Button, Icon },
    setup() {
      return { args };
    },
    template: `
      <Button v-bind="args">
        <template #icon>
          <Icon id="user" size="regular" />
        </template>
      </Button>
    `,
  }),
};
