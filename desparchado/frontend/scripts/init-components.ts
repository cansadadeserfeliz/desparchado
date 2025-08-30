/**
 * Initialize components inside a root
 * @param {ParentNode} root
 */
// Add a constructor type for components
type ComponentCtor = new (el: HTMLElement) => unknown;

export function initComponents(
  root: ParentNode = document,
  registry: Map<string, ComponentCtor>
): void {
  const nodes = root.querySelectorAll<HTMLElement>('[data-component]');
  nodes.forEach((el: HTMLElement) => {
    const componentName = el.getAttribute('data-component');
    if (!componentName) return;

    const ComponentClass = registry.get(componentName);
    if (!ComponentClass) {
      console.warn(`initComponents: component "${componentName}" not found in registry`);
      return;
    }

    try {
      new ComponentClass(el);
    } catch (err) {
      console.error(`initComponents: failed to init "${componentName}"`, err);
    }
  });
}
}
