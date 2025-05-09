import MenuDropdown from '@presentational_components/components/menu-dropdown/MenuDropdown.vue';
import Button from '@presentational_components/atoms/button/Button.vue';
import Icon from '@presentational_components/foundation/icon/Icon.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/MenuDropdown',
  component: MenuDropdown,
  tags: ['autodocs'],
  argTypes: {
    items: {
      control: 'object',
    },
  },
  args: {
    items: [
      { label: 'Ver mi perfil', url: 'item1' },
      { label: 'Eventos agregados', url: 'item2' },
    ],
  },
} satisfies Meta<typeof MenuDropdown>;

export default meta;

type Story = StoryObj<typeof meta>;

export const MenuDropdownProfile: Story = {
  args: {
    items: [
      { label: 'Ver mi perfil', url: 'item1' },
      { label: 'Eventos agregados', url: 'item2' },
    ],
  },
  render: (args) => ({
    components: { MenuDropdown, Button, Icon },
    setup() {
      return { args };
    },
    template: `
    <MenuDropdown v-bind="args">
      <template #trigger>
        <Button type="primary" padding="balanced">
          <template #icon>
            <Icon id="user" size="regular" />
          </template>
        </Button>
      </template>
    </MenuDropdown>
    `,
  }),
};
