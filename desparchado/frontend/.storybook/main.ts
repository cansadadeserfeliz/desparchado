import type { StorybookConfig } from '@storybook/vue3-vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

const config: StorybookConfig = {
  framework: {
    name: '@storybook/vue3-vite',
    options: {},
  },
  stories: [
    '../stories/**/*.stories.@(js|ts)',
    "../stories/**/*.mdx",
  ],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-onboarding",
    "@chromatic-com/storybook",
    "@storybook/experimental-addon-test"
  ],
  viteFinal: async (config) => {
    config.plugins = [...(config.plugins || []), vue()];

    config.resolve = {
      alias: {
        "@presentational_components": resolve(__dirname, "../components/presentational"),
        "@styles": resolve(__dirname, "../styles"),
        "@fonts": resolve(__dirname, "../assets/fonts")
      }
    };
    return config;
  },
};

export default config;
