import Overlay from '@presentational_components/components/Overlay/Overlay.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/Overlay',
  component: Overlay,
  tags: ['autodocs'],
  argTypes: {
    show: { control: 'boolean' },
    closeLabel: { control: 'text' },
    customClass: { control: 'text' },
    dialogLabel: { control: 'text' },
    labelledBy: { control: 'text' },
    loading: { control: 'boolean' },
    loadingText: { control: 'text' },
  },
  args: {
    show: true,
    closeLabel: 'Cerrar',
    customClass: '',
    dialogLabel: '',
    labelledBy: '',
    loading: false,
    loadingText: 'Guardando...',
  },
} satisfies Meta<typeof Overlay>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => ({
    components: { Overlay },
    setup() {
      return { args };
    },
    template: `
      <Overlay v-bind="args">
        <div style="padding: 20px; text-align: center;">
          <h3 style="margin-top: 0;">Overlay Content</h3>
          <p>This is a reusable overlay modal component.</p>
        </div>
      </Overlay>
    `,
  }),
};

export const Loading: Story = {
  args: {
    show: true,
    loading: true,
    loadingText: 'Guardando evento...',
    dialogLabel: 'Guardando cambios',
  },
};
