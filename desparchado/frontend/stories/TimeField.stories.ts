import TimeField from '@presentational_components/components/TimeField/TimeField.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/TimeField',
  component: TimeField,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'text' },
    id: { control: 'text' },
    label: { control: 'text' },
    hideLabel: { control: 'boolean' },
    customClass: { control: 'text' },
    required: { control: 'boolean' },
    errors: { control: 'object' },
  },
  args: {
    id: 'time-field-demo',
    modelValue: '',
    label: 'Fecha y Hora',
    hideLabel: false,
    customClass: '',
  },
} satisfies Meta<typeof TimeField>;

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
    // Expected in America/Bogota (UTC-5 offset) ISO format
    modelValue: '2026-07-15T19:00:00-05:00',
  },
};

export const WithErrors: Story = {
  args: {
    modelValue: '',
    errors: ['Este campo es requerido'],
  },
};
