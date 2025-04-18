document.addEventListener("DOMContentLoaded", function () {

  // Mark sub-header menu element as active
  document.querySelectorAll(".users-sub-header a").forEach(function (link) {
    const currentPath = link.getAttribute("href");
    if (
      currentPath === window.location.pathname ||
      window.location.pathname.startsWith(currentPath)
    ) {
      const li = link.closest("li");
      if (li) li.classList.add("active");
    }
  });

  function showSuggestion(suggestionMessage) {
    const feedbackSpan = document.createElement("span");
    feedbackSpan.className = "suggestions-feedback text-warning";
    feedbackSpan.innerHTML = suggestionMessage;

    const triggerElem = document.querySelector(".show-suggestions");
    if (triggerElem) {
      triggerElem.insertAdjacentElement("afterend", feedbackSpan);
    }
  }

  function hideSuggestions() {
    document.querySelectorAll(".suggestions-feedback").forEach(el => el.remove());
  }

  const inputElem = document.querySelector(".show-suggestions");
  if (inputElem) {
    inputElem.addEventListener("keydown", function () {
      const suggestionsUrl = inputElem.dataset.suggestionsUrl;
      const query = inputElem.value;

      console.log(inputElem);
      console.log(suggestionsUrl);
      console.log(query);

      fetch(`${suggestionsUrl}?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
          console.log(data.suggestion);
          hideSuggestions();
          if (data.suggestion) {
            showSuggestion(data.suggestion);
          }
        })
        .catch(error => console.error("Error fetching suggestion:", error));
    });
  }

});
