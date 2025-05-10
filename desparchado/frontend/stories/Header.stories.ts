import Header from '@presentational_components/components/header/Header.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/Header',
  component: Header,
  tags: ['autodocs'],
  argTypes: {
    navItems: { control: 'object' },
    social: { control: 'object' },
    isLogged: { control: 'boolean' },
  },
  args: {},
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof Header>;

export default meta;

type Story = StoryObj<typeof meta>;

export const MainHeader: Story = {
  args: {
    navItems: [
      { label: 'Eventos', link: '/events' },
      { label: 'Archivo', link: '/archive', highlight: true },
    ],
    social: [
      { type: 'tertiary', name: 'Facebook', link: 'https://www.facebook.com/', icon: 'xsocial' },
      {
        type: 'tertiary',
        padding: 'balanced',
        name: 'Instagram',
        link: 'https://www.instagram.com/',
        icon: 'facebook',
      },
      { type: 'tertiary', name: 'Twitter', link: 'https://twitter.com/', icon: 'instagram' },
    ],
    profileMenu: {
      items: [
        { label: 'Ver mi perfil', url: 'item1' },
        { label: 'Eventos agregados', url: 'item2' },
      ],
      name: 'perfil',
    },
    login: {
      label: 'Iniciar sesión',
      link: '/login',
      type: 'tertiary',
    },
    createEvent: {
      label: 'Crear evento',
      link: '/events/add',
      type: 'primary',
    },
    brandName: 'Desparchado',
  },
};
