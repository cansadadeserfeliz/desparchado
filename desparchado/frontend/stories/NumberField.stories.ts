import NumberField from '@presentational_components/components/NumberField/NumberField.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/NumberField',
  component: NumberField,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'text' },
    id: { control: 'text' },
    label: { control: 'text' },
    hideLabel: { control: 'boolean' },
    customClass: { control: 'text' },
    placeholder: { control: 'text' },
    required: { control: 'boolean' },
    min: { control: 'number' },
    errors: { control: 'object' },
  },
  args: {
    id: 'number-field-demo',
    modelValue: '',
    label: 'Precio (COP)',
    placeholder: 'Ej. 15000',
    hideLabel: false,
    customClass: '',
    min: 0,
  },
} satisfies Meta<typeof NumberField>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const Required: Story = {
  args: {
    required: true,
  },
};

export const WithValue: Story = {
  args: {
    modelValue: 25000,
  },
};

export const WithErrors: Story = {
  args: {
    modelValue: -100,
    errors: ['El precio no puede ser negativo'],
  },
};
