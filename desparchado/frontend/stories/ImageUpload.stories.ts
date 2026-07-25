import ImageUpload from '@presentational_components/components/ImageUpload/ImageUpload.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/ImageUpload',
  component: ImageUpload,
  tags: ['autodocs'],
  argTypes: {
    id: { control: 'text' },
    label: { control: 'text' },
    hideLabel: { control: 'boolean' },
    maxSizeMb: { control: 'number' },
    disabled: { control: 'boolean' },
    condensed: { control: 'boolean' },
    required: { control: 'boolean' },
    errors: { control: 'text' },
  },
  args: {
    id: 'image-upload-demo',
    label: 'Imagen del evento',
    hideLabel: false,
    modelValue: null,
    previewUrl: '',
    maxSizeMb: 10,
    disabled: false,
    condensed: false,
    required: false,
  },
} satisfies Meta<typeof ImageUpload>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const WithPreview: Story = {
  args: {
    previewUrl: 'https://picsum.photos/400/250',
  },
};

export const Condensed: Story = {
  args: {
    condensed: true,
  },
};

export const WithError: Story = {
  args: {
    errors: ['La imagen supera el límite de 10MB.'],
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};
