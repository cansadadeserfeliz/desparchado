import '../../frontend/styles/legacy_styles.scss';


document.addEventListener('DOMContentLoaded', () => {
  // Mark sub-header menu element as active
  const subHeaderLinks = document.querySelectorAll<HTMLAnchorElement>('.users-sub-header a');

  subHeaderLinks.forEach((link) => {
    const currentPath = link.getAttribute('href');
    const pathname = window.location.pathname;
    if (
      currentPath &&
      (pathname === currentPath || pathname.startsWith(currentPath))
    ) {
      const parentLi = link.closest('li');
      if (parentLi) {
        parentLi.classList.add('active');
      }
    }
  });

  function showSuggestion(suggestionMessage: string): void {
    const suggestionInput = document.querySelector('.show-suggestions');
    if (suggestionInput) {
      const feedback = document.createElement('span');
      feedback.className = 'suggestions-feedback text-warning';
      feedback.innerHTML = suggestionMessage;
      suggestionInput.insertAdjacentElement('afterend', feedback);
    }
  }

  function hideSuggestions(): void {
    document.querySelectorAll('.suggestions-feedback').forEach(el => el.remove());
  }

  const showSuggestionInput = document.querySelector<HTMLInputElement>('.show-suggestions');

  if (showSuggestionInput) {
    showSuggestionInput.addEventListener('keydown', () => {
      const url = showSuggestionInput.dataset.suggestionsUrl;
      const query = showSuggestionInput.value;

      if (!url) return;

      fetch(`${url}?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then((data: { suggestion?: string }) => {
          hideSuggestions();
          if (data.suggestion) {
            showSuggestion(data.suggestion);
          }
        })
        .catch((error) => {
          console.error('Suggestion fetch error:', error);
        });
    });
  }
});
