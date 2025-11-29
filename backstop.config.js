const USE_PROD = false; // change to true when you want production

const BASE_URL = USE_PROD
  ? "https://desparchado.co"
  : "http://localhost:8000";

const IGNORE_DEBUG_TOOLBAR = !USE_PROD;
const debugRemoveSelectors = IGNORE_DEBUG_TOOLBAR
  ? ["#djDebug", ".djDebug"]
  : [];

module.exports = {
  "id": "desparchado",
  "viewports": [
    {
      "label": "phone",
      "width": 320,
      "height": 480
    },
    {
      "label": "tablet",
      "width": 1024,
      "height": 768
    },
    {
      "label": "desktop",
      "width": 1440,
      "height": 900
    }
  ],
  "onBeforeScript": "puppet/onBefore.js",
  "onReadyScript": "puppet/onReady.js",
  "scenarios": [
    {
      "label": "Home",
      "cookiePath": "backstop_data/engine_scripts/cookies.json",
      "url": `${BASE_URL}/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "delay": 0,
      "hideSelectors": [],
      "removeSelectors": [
        ...debugRemoveSelectors,
        ".event-card__details .event-card__image",
        ".event-card__details .event-card__location",
        ".event-card__details .event-card__day",
        ".event-card__details .event-card__time",
        ".event-card__details .rich-text-description",
        ".featured-events .featured-events__item .featured-event-card__image",
        ".featured-events .featured-events__item .featured-event-card__location",
        ".featured-events .featured-events__item .featured-event-card__date-copy",
        ".featured-events .featured-events__item .featured-event-card__title",
        ".featured-events .featured-events__item .featured-event-card__day",
        ".featured-events .featured-events__item .featured-event-card__time"
      ],
      "hoverSelector": "",
      "clickSelector": "",
      "postInteractionWait": 0,
      "selectors": [],
      "selectorExpansion": true,
      "expect": 0,
      "misMatchThreshold" : 0.1,
      "requireSameDimensions": true
    },
    {
      "label": "Events list",
      "cookiePath": "backstop_data/engine_scripts/cookies.json",
      "url": `${BASE_URL}/events/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "delay": 0,
      "hideSelectors": [],
      "removeSelectors": [
        ...debugRemoveSelectors,
        ".event-card-full-width .event-card-full-width__image",
        ".event-card-full-width .event-card-full-width__location",
        ".event-card-full-width .event-card-full-width__date-copy",
        ".event-card-full-width .event-card-full-width__title",
        ".event-card-full-width .event-card-full-width__day",
        ".event-card-full-width .event-card-full-width__time",
        ".event-card-full-width .rich-text-description"
      ],
      "hoverSelector": "",
      "clickSelector": "",
      "postInteractionWait": 0,
      "selectors": [],
      "selectorExpansion": true,
      "expect": 0,
      "misMatchThreshold" : 0.1,
      "requireSameDimensions": true
    },
    {
      "label": "Event detail",
      "cookiePath": "backstop_data/engine_scripts/cookies.json",
      "url": `${BASE_URL}/events/la-novela-virgenes-y-toxicomanos-de-mario-mendoza/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "delay": 0,
      "hideSelectors": [],
      "removeSelectors": [
        ...debugRemoveSelectors,
        ".featured-events .featured-events__item .featured-event-card__image",
        ".featured-events .featured-events__item .featured-event-card__location",
        ".featured-events .featured-events__item .featured-event-card__date-copy",
        ".featured-events .featured-events__item .featured-event-card__title",
        ".featured-events .featured-events__item .featured-event-card__day",
        ".featured-events .featured-events__item .featured-event-card__time",
        ".event-detail time",
        ".event-detail img"
      ],
      "hoverSelector": "",
      "clickSelector": "",
      "postInteractionWait": 0,
      "selectors": [],
      "selectorExpansion": true,
      "expect": 0,
      "misMatchThreshold" : 0.1,
      "requireSameDimensions": true
    },
    {
      "label": "Header",
      "cookiePath": "backstop_data/engine_scripts/cookies.json",
      "url": `${BASE_URL}/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "delay": 0,
      "hideSelectors": [],
      "removeSelectors": [
        ...debugRemoveSelectors
      ],
      "hoverSelector": "",
      "clickSelector": "",
      "postInteractionWait": 0,
      "selectors": [".header"],
      "selectorExpansion": true,
      "expect": 0,
      "misMatchThreshold" : 0.1,
      "requireSameDimensions": true
    }
  ],
  "paths": {
    "bitmaps_reference": "backstop_data/bitmaps_reference",
    "bitmaps_test": "backstop_data/bitmaps_test",
    "engine_scripts": "backstop_data/engine_scripts",
    "html_report": "backstop_data/html_report",
    "ci_report": "backstop_data/ci_report"
  },
  "report": ["browser"],
  "engine": "puppeteer",
  "engineOptions": {
    "args": ["--no-sandbox"]
  },
  "asyncCaptureLimit": 5,
  "asyncCompareLimit": 50,
  "debug": false,
  "debugWindow": false
}
