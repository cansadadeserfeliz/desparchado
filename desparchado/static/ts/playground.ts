import '../../frontend/styles/playground.scss';
  document.addEventListener('DOMContentLoaded', () => {
    requestAnimationFrame(() => {
      const header = document.getElementById('header');
      const height = header?.offsetHeight;
      document.body.style.setProperty('--header-height', `${height}px`);
    });
  });
