(() => {

  function LetterAvatar(name = '', size = 60) {
    const colors = [
      "#1abc9c", "#2ecc71", "#3498db", "#9b59b6", "#34495e", "#16a085", "#27ae60", "#2980b9",
      "#8e44ad", "#2c3e50", "#f1c40f", "#e67e22", "#e74c3c", "#ecf0f1", "#95a5a6",
      "#f39c12", "#d35400", "#c0392b", "#bdc3c7", "#7f8c8d"
    ];

    const nameParts = name.toUpperCase().split(' ');
    const initials = nameParts.length === 1
      ? nameParts[0]?.charAt(0) || '?'
      : nameParts[0].charAt(0) + nameParts[1].charAt(0);

    if (window.devicePixelRatio) {
      size *= window.devicePixelRatio;
    }

    const charIndex = (initials === '?' ? 72 : initials.charCodeAt(0)) - 64;
    const colorIndex = charIndex % colors.length;

    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;

    const ctx = canvas.getContext('2d');
    ctx.fillStyle = colors[colorIndex];
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.font = `${Math.round(canvas.width / 2)}px Arial`;
    ctx.textAlign = 'center';
    ctx.fillStyle = '#FFF';
    ctx.fillText(initials, size / 2, size / 1.5);

    const dataURI = canvas.toDataURL();
    return dataURI;
  }

  function transformLetterAvatars() {
    document.querySelectorAll('img[avatar]').forEach(img => {
      const name = img.getAttribute('avatar');
      const width = parseInt(img.getAttribute('width'), 10) || 60;
      img.src = LetterAvatar(name, width);
      img.removeAttribute('avatar');
      img.setAttribute('alt', name);
    });
  }

  // Export as a global, module, or define as needed
  if (typeof define === 'function' && define.amd) {
    define(() => LetterAvatar);
  } else if (typeof module !== 'undefined' && module.exports) {
    module.exports = LetterAvatar;
  } else {
    window.LetterAvatar = LetterAvatar;
    document.addEventListener('DOMContentLoaded', transformLetterAvatars);
  }

})();
