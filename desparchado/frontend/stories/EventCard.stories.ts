import EventCard from '@presentational_components/components/event-card/EventCard.vue';
import type { Decorator, Meta, StoryObj } from '@storybook/vue3';

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories
const meta = {
  title: 'Components/EventCard',
  component: EventCard,
  tags: ['autodocs'],
  argTypes: {
    tag: {
      control: 'select',
      options: ['div', 'li', 'section', 'article'],
    },
  },
  args: {
    tag: 'div',
  },
} satisfies Meta<typeof EventCard>;

export default meta;

type Story = StoryObj<typeof meta>;

export const NormalCard: Story = {
  args: {
    tag: 'div',
    location: 'Biblioteca Luis Ángel Aranjo',
    description: `<p> </p><p><a href="https://blaa.checkout.tuboleta.com/selection/event/date?productId=10230025721105" target="_blank" title="Comprar" rel="noopener">Comprar boletas en línea</a></p><p>Nació en Bucaramanga e inició sus estudios en formación vocal y coral a los once años con el maestro Juan Manuel Hernández Morales. Cursó el pregrado en música de la Universidad Autónoma de Bucaramanga con énfasis en Canto lírico. Con el coro UNAB realizó giras en Estados Unidos y Europa y ha sido solista del Ensamble Lírico UNAB, la Orquesta Sinfónica UNAB y la Orquesta Sinfónica Juvenil UNAB. Ha recibido clases magistrales con Alejandro Roca, Maurizio Leoni, Ximena Bernal, Hans Mogollón y Sara Catarine. Actualmente cursa la maestría en educación de la UNAB y es docente de la cátedra de canto de la Universidad de Pamplona. Presenta un programa con música de Franz Schubert, Jaime León, Heitor Villa-Lobos, W.A. Mozart y G.F. Händel, entre otros, en compañía del pianista <strong>Alfredo Saad Corredor</strong>.</p>Programa<p>Alberto Ginastera: Cinco canciones populares argentinas <br>Franz Schubert: Gretchem am Spinnrade; Du bist die Ruh <br>Jaime León: Algún día; La campesina <br>Heitor Villa-lobos: Bachianas brasileras No. 5  <br>Georg Friedrich Händel: Aria de <em>El Mesías  </em><br>Wolfgang Amadeus Mozart: Arias de <em>Le Nozze Di Figaro  </em><br>Vincenzo Bellini: Aria de<em> I Capuleti e i Montecchi  </em><br>Benjamin Britten: Paul Bunyan <br> </p><p> </p>Conoce más acerca del artista<p><a href="https://www.youtube.com/@MayraVargasSoprano">Canal en YouTube »</a><br><a href="https://www.facebook.com/MayraVargasSoprano/">Página en Facebook »</a><br><a href="https://www.instagram.com/mayravargassoprano/">Página en Instagram »</a></p><p>PULEP: LQA956</p> Jueves, 6:30 pm - 8:30 pm <h2>Boletería</h2><p> <a href="https://www.tuboleta.com/images/Eventos/Biblioteca-luis-angel-arango-sala-de-conciertos/index.html" target="_blank" title="Comprar boletas" rel="noopener">Compra en línea</a></p><p> </p><h3>Taquilla</h3><p>Biblioteca Luis Ángel Arango</p><p>Calle 11 # 4 - 14 · Bogotá D. C.</p><p>Lunes a sábado: 11:00 a. m. a 7:00 p. m.<br>Domingos: 9:00 a. m. a 4:00 p. m.</p><p> </p><p><strong>Horario extendido los días de concierto:</strong></p><p>Miércoles: 11:00 a. m. a 8:00 p. m.<br>Jueves: 11:00 a. m. a 7:30 p. m.</p><p> </p><p><strong>Teléfono:</strong> 601 381 2929</p><p> </p><p>Servicio ofrecido por:</p><p> <a href="https://www.tuboleta.com/images/Eventos/Biblioteca-luis-angel-arango-sala-de-conciertos/index.html"></a></p><p> </p><p><a href="https://www.banrepcultural.org/servicios/boleteria-conciertos">Conoce las tarifas y descuentos »</a></p> <p>Edad mínima recomendada: siete (7) años. Por disposiciones de la Secretaría Distrital de Gobierno no se permite el acceso de menores de cinco (5) años.</p> <hr> <p><a href="https://www.banrepcultural.org/actividad-musical/la-sala/programa-tu-visita" target="_blank" rel="noopener">Programa tu visita a la Sala de Conciertos »</a></p>`,
    title: 'No estamos solos la paz también se hace con animales',
    day: '17 Jun',
    time: '22:00',
    link: '/event-card/',
  },
  decorators: [
    (() => ({
      template: `
      <div style="height: 500px;">
        <story />
      </div>
    `,
    })) as Decorator,
  ],
};
