/**
 * Initialize components inside a root
 * @param {ParentNode} root
 */
export function initComponents(root: ParentNode = document, registry: Map<string, unknown>): void {
  const nodes = root.querySelectorAll('[data-component]');
  nodes.forEach((el) => {
    const componentName = el.getAttribute('data-component');
    if (!componentName) return;

    const ComponentClass = registry.get(componentName);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    new (ComponentClass as any)(el);
  });
}
