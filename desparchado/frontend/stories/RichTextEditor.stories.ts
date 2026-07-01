import RichTextEditor from '@presentational_components/components/RichTextEditor/RichTextEditor.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/RichTextEditor',
  component: RichTextEditor,
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
    id: 'rich-text-editor-demo',
    modelValue: '',
    label: 'Descripción del Evento',
    placeholder: 'Describe de qué se trata el evento...',
    hideLabel: false,
    customClass: '',
  },
} satisfies Meta<typeof RichTextEditor>;

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

export const Prepopulated: Story = {
  args: {
    modelValue:
      '<p>Este es un texto con <strong>negrita</strong>, <em>cursiva</em> y <u>subrayado</u>.</p><ul><li>Elemento 1</li><li>Elemento 2</li></ul>',
  },
};

export const WithCustomClass: Story = {
  args: {
    customClass: 'wizard-field',
  },
};

export const WithErrors: Story = {
  args: {
    errors: [
      'La descripción no puede estar vacía',
      'La descripción contiene palabras no permitidas',
    ],
  },
};
