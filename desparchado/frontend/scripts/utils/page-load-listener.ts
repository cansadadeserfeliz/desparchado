import { ComponentCtor, initComponents } from '../init-components';

export const attachOnLoadListener = (registry: Map<string, ComponentCtor>): void => {
  document.addEventListener('DOMContentLoaded', () => {
    const updateHeaderHeight = (): void => {
      requestAnimationFrame(() => {
        const header = document.getElementById('header');
        const height = header?.offsetHeight;
        if (height) {
          document.body.style.setProperty('--header-height', `${height}px`);
        }
      });
    };

    // Set initial height
    updateHeaderHeight();

    // Update on resize
    window.addEventListener('resize', updateHeaderHeight);

    window.addEventListener('button:action:logout', () => {
      const form = document.getElementById('logout-form');
      if (form instanceof HTMLFormElement) {
        form.submit();
      }
    });

    initComponents(document, registry);
  });
};
