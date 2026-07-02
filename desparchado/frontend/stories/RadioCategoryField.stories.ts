import RadioCategoryField from '@presentational_components/components/RadioCategoryField/RadioCategoryField.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/RadioCategoryField',
  component: RadioCategoryField,
  tags: ['autodocs'],
  argTypes: {
    modelValue: { control: 'text' },
    id: { control: 'text' },
    customClass: { control: 'text' },
  },
  args: {
    id: 'radio-category-field-demo',
    modelValue: 'other',
    customClass: '',
  },
} satisfies Meta<typeof RadioCategoryField>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const LiteratureSelected: Story = {
  args: {
    modelValue: 'literature',
  },
};

export const ArtSelected: Story = {
  args: {
    modelValue: 'art',
  },
};
