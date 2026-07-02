import ToggleField from '@presentational_components/components/ToggleField/ToggleField.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/ToggleField',
  component: ToggleField,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'boolean' },
    id: { control: 'text' },
    label: { control: 'text' },
    customClass: { control: 'text' },
  },
  args: {
    id: 'toggle-field-demo',
    modelValue: false,
    label: 'Publicar evento inmediatamente',
    customClass: '',
  },
} satisfies Meta<typeof ToggleField>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const Checked: Story = {
  args: {
    modelValue: true,
  },
};
