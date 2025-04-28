import type { Meta, StoryObj } from '@storybook/vue3';

import Heading from '../components/presentational/foundation/heading/Heading.vue';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/Heading',
  component: Heading,
  tags: ['autodocs'],
  argTypes: {
    tag: {
      control: 'select',
      options: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    },
    type: {
      control: 'select',
      options: ['h1', 'h2', 'h3', 'h4', 'h5', 's1'],
    },
    weight: {
      control: 'select',
      options: ['regular', 'medium', 'bold'],
    },
  },
  args: {
    tag: 'h1',
    type: 'h1',
    weight: 'regular',
  },
} satisfies Meta<typeof Heading>;

export default meta;

type Story = StoryObj<typeof meta>;

export const H1: Story = {
  args: {
    tag: 'h1',
    type: 'h1',
    weight: 'bold',
    text: 'Heading 1',
    id: 'head1',
  },
};

export const Subtitle1: Story = {
  args: {
    tag: 'h1',
    type: 's1',
    text: 'Subtitle 1',
    id: 'sub1',
  },
};

export const H2: Story = {
  args: {
    tag: 'h2',
    type: 'h2',
    text: 'Heading 2',
    id: 'head2',
  },
};

export const H3: Story = {
  args: {
    tag: 'h3',
    type: 'h3',
    weight: 'medium',
    text: 'Heading 3',
    id: 'head3',
  },
};

export const H4: Story = {
  args: {
    tag: 'h4',
    type: 'h4',
    text: 'Heading 4',
    id: 'head4',
  },
};

export const H5: Story = {
  args: {
    tag: 'h5',
    type: 'h5',
    text: 'Heading 5',
    id: 'head5',
  },
};
