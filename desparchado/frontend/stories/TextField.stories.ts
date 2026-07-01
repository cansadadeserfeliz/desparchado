import TextField from '@presentational_components/components/TextField/TextField.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/TextField',
  component: TextField,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'text' },
    id: { control: 'text' },
    label: { control: 'text' },
    hideLabel: { control: 'boolean' },
    customClass: { control: 'text' },
    placeholder: { control: 'text' },
    required: { control: 'boolean' },
    errors: { control: 'object' },
  },
  args: {
    id: 'text-field-demo',
    modelValue: '',
    label: 'Título del Evento',
    placeholder: 'Ej. Concierto de Jazz en el Parque',
    hideLabel: false,
    customClass: '',
  },
} satisfies Meta<typeof TextField>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const VisuallyHiddenLabel: Story = {
  args: {
    hideLabel: true,
  },
};

export const WithCustomClass: Story = {
  args: {
    customClass: 'wizard-field',
  },
};

export const Required: Story = {
  args: {
    required: true,
  },
};

export const WithErrors: Story = {
  args: {
    modelValue: 'Texto inválido',
    errors: ['El título no puede contener caracteres especiales', 'El título es demasiado largo'],
  },
};
