import { createApp, Component } from 'vue';

/**
 * Auto-import all Vue components from the specified folder using Vite's glob import.
 * Eager mode ensures components are immediately available without dynamic import.
 */
const files = import.meta.glob('@presentational_components/**/*.vue', {
  eager: true,
});

/**
 * Converts a PascalCase or camelCase string to kebab-case.
 *
 * @param {string} str - The input string (e.g. "CardSimple")
 * @returns {string} The transformed kebab-case string (e.g. "card-simple")
 */
function toKebabCase(str: string): string {
  return str
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/([A-Z])([A-Z][a-z])/g, '$1-$2')
    .toLowerCase();
}

/**
 * Map of all available components using kebab-case keys.
 * Example: { 'card-simple': CardSimpleComponent }
 */
const components: Record<string, Component> = {};

// Populate the components map with auto-imported components
for (const path in files) {
  const match = path.match(/\/([A-Za-z0-9_-]+)\.vue$/);
  if (match) {
    const kebabName = toKebabCase(match[1]);
    components[kebabName] = (files[path] as { default: Component }).default;
  }
}

/**
 * Mounts Vue components dynamically to DOM elements using data attributes.
 */
class VueComponentMount {
  private readonly components: Record<string, Component>;

  /**
   * @param {Record<string, Component>} components - A map of kebab-case component names to Vue components
   */
  constructor(components: Record<string, Component>) {
    this.components = components;
  }

  /**
   * Finds all elements with `data-vue-component` and mounts the matching Vue component.
   * Props are passed using `data-vue-prop-[propName]` attributes.
   */
  public mountAll(): void {
    const elements = document.querySelectorAll<HTMLElement>('[data-vue-component]');

    elements.forEach((el) => {
      const componentName = el.dataset.vueComponent?.toLowerCase() as string;
      if (!componentName) return;

      const component = this.components[componentName];
      if (!component) {
        console.warn(`Vue component "${componentName}" not found!`);
        return;
      }

      const props = this.extractProps(el);
      createApp(component, props).mount(el);
    });
  }

  /**
   * Extracts props from `data-vue-prop-*` attributes on a DOM element.
   *
   * @param {HTMLElement} el - The element containing prop attributes
   * @returns {Record<string, unknown>} An object of prop key-value pairs
   */
  private extractProps(el: HTMLElement): Record<string, unknown> {
    const props: Record<string, unknown> = {};

    Array.from(el.attributes).forEach((attr) => {
      const match = attr.name.match(/^data-vue-prop-(.+)$/);
      if (match) {
        const propName = match[1];
        props[propName] = attr.value;
      }
    });

    return props;
  }
}

// Create an instance using the auto-registered components
const vueMount = new VueComponentMount(components);

/**
 * Wait for DOMContentLoaded to ensure all elements are present before mounting.
 */
document.addEventListener('DOMContentLoaded', () => {
  try {
    vueMount.mountAll();
    console.info(`Successfully mounted ${Object.keys(components).length} Vue component types`);
  } catch (error) {
    console.error('Error mounting Vue components:', error);
  }
});
