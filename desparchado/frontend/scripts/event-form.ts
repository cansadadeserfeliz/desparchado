import { createApp } from 'vue';
import EventWizardCreate from '@presentational_components/containers/event-wizard/EventWizardCreate/EventWizardCreate.vue';
import EventWizardEdit from '@presentational_components/containers/event-wizard/EventWizardEdit/EventWizardEdit.vue';

document.addEventListener('DOMContentLoaded', () => {
  const el = document.querySelector<HTMLElement>('[data-vue-component="event-wizard"]');
  if (!el) {
    console.error('Mount element [data-vue-component="event-wizard"] not found.');
    return;
  }

  const wizardMode = el.getAttribute('data-wizard-mode') ?? 'create';
  const apiUrl = el.getAttribute('data-api-url') ?? '';
  const apiUpdateUrl = el.getAttribute('data-api-update-url') ?? '';

  let cities = [];
  const citiesRaw = el.getAttribute('data-vue-prop-cities');
  if (citiesRaw) {
    try {
      cities = JSON.parse(citiesRaw);
    } catch (e) {
      console.error('Error parsing cities JSON:', e);
    }
  }

  const props = {
    wizardMode,
    apiUrl,
    apiUpdateUrl,
    cities,
  };

  const component = wizardMode === 'edit' ? EventWizardEdit : EventWizardCreate;
  createApp(component, props).mount(el);
});
