import SearchableCombobox from '@presentational_components/components/SearchableCombobox/SearchableCombobox.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/SearchableCombobox',
  component: SearchableCombobox,
  tags: ['autodocs'],
  argTypes: {
    id: { control: 'text' },
    label: { control: 'text' },
    placeholder: { control: 'text' },
    searchUrl: { control: 'text' },
    multiple: { control: 'boolean' },
    required: { control: 'boolean' },
    hideLabel: { control: 'boolean' },
    errors: { control: 'object' },
  },
  args: {
    id: 'searchable-combobox-demo',
    label: 'Organizador',
    placeholder: 'Buscar organizador...',
    searchUrl: '/events/api/v1/organizers/search/',
    modelValue: null,
    multiple: false,
    required: false,
    hideLabel: false,
  },
} satisfies Meta<typeof SearchableCombobox>;

export default meta;
type Story = StoryObj<typeof meta>;

export const DefaultSingle: Story = {
  args: {},
};

export const MultiSelect: Story = {
  args: {
    label: 'Organizadores',
    placeholder: 'Buscar organizadores...',
    multiple: true,
    modelValue: [],
  },
};

export const WithPreselectedOptions: Story = {
  args: {
    label: 'Organizadores',
    multiple: true,
    modelValue: [1, 2],
    initialOptions: [
      { id: 1, name: 'Fundación Filarmónica de Bogotá' },
      { id: 2, name: 'Biblioteca Luis Ángel Arango' },
    ],
  },
};

export const Required: Story = {
  args: {
    required: true,
  },
};

export const WithErrors: Story = {
  args: {
    required: true,
    errors: ['Debe seleccionar al menos un organizador.'],
  },
};
