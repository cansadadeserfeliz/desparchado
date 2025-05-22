import '../styles/playground.scss';

  document.addEventListener('DOMContentLoaded', () => {
    requestAnimationFrame(() => {
      const header = document.getElementById('header');
      console.log(header);
      const height = header?.offsetHeight;
      console.log(height);
      document.body.style.setProperty('--header-height', `${height}px`);

    });
  });
