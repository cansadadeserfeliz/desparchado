import type { Preview } from '@storybook/vue3';
import '../styles/index.scss';
import { MINIMAL_VIEWPORTS } from '@storybook/addon-viewport';


const preview: Preview = {
  parameters: {
    layout: 'centered',
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    viewport: {
      viewports: {
        ...MINIMAL_VIEWPORTS,
      },
      defaultViewport: 'large',
    },
  },
};

export default preview;
