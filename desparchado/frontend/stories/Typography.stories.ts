import Typography from '@presentational_components/foundation/typography/Typography.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/Typography',
  component: Typography,
  tags: ['autodocs'],
  argTypes: {
    tag: {
      control: 'select',
      options: ['span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    },
    type: {
      control: 'select',
      options: [
        'body_sm',
        'body_md',
        'body_lg',
        'body_highlight',
        'caption',
        'header_item',
        'h1',
        'h2',
        'h3',
        'h4',
        'h5',
        's1',
      ],
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
} satisfies Meta<typeof Typography>;

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

export const BodySm: Story = {
  args: {
    tag: 'p',
    type: 'body_sm',
    text: 'Body Small',
    id: 'body_sm',
  },
};

export const BodyMd: Story = {
  args: {
    tag: 'p',
    type: 'body_md',
    text: 'Body Medium',
    id: 'body_md',
  },
};

export const BodyLg: Story = {
  args: {
    tag: 'p',
    type: 'body_lg',
    text: 'Body Large',
    id: 'body_lg',
  },
};

export const BodyHighlight: Story = {
  args: {
    tag: 'p',
    type: 'body_highlight',
    text: 'Body Highlight',
    id: 'bodyhighlight',
  },
};

export const Caption: Story = {
  args: {
    tag: 'span',
    type: 'caption',
    text: 'Caption',
    id: 'caption',
  },
};

export const HeaderItem: Story = {
  args: {
    tag: 'span',
    type: 'header_item',
    text: 'Header Item',
    id: 'headeritem',
  },
};
