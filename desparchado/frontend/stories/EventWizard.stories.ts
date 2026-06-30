import EventWizard from '@presentational_components/containers/event-wizard/EventWizard/EventWizard.vue';
import type { Meta, StoryObj } from '@storybook/vue3';

const meta = {
  title: 'Components/EventWizard',
  component: EventWizard,
  tags: ['autodocs'],
  argTypes: {
    mode: {
      control: 'select',
      options: ['create', 'edit'],
    },
  },
  args: {
    mode: 'create',
    apiUrl: '/mock-api/events/',
    apiUpdateUrl: '/mock-api/events/mock-slug/',
    cities: [
      { id: 1, name: 'Bogotá' },
      { id: 2, name: 'Medellín' },
      { id: 3, name: 'Cali' },
      { id: 4, name: 'Barranquilla' },
    ],
  },
} satisfies Meta<typeof EventWizard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const CreateMode: Story = {
  args: {
    mode: 'create',
  },
};

const descriptionHtml =
  '<p>Acompáñanos en la inauguración del festival más grande de las letras.</p>';

export const EditMode: Story = {
  args: {
    mode: 'edit',
    initialData: {
      title: 'Lanzamiento del Festival de Literatura 2026',
      description: descriptionHtml,
      category: 'literature',
      price: '15000',
      event_source_url: 'https://desparchado.co/festival-lit-2026',
      is_published: true,
      event_date: '2026-07-15T19:00:00',
      organizers: [{ id: 1, name: 'Asociación de Escritores Colombianos' }],
      speakers: [{ id: 2, name: 'Laura Restrepo' }],
      place: {
        id: 5,
        name: 'Biblioteca Luis Ángel Arango',
        city: 1,
      },
      image_url: 'https://picsum.photos/id/101/800/600',
    },
  },
};
