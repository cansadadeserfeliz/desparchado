/* eslint-env node */

const isProd = process.argv.includes("--prod");

const BASE_URL = isProd
  ? "https://desparchado.co"
  : "http://localhost:8000";

const IGNORE_DEBUG_TOOLBAR = !isProd;
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
  "scenarioDefaults": {
    "cookiePath": "backstop_data/engine_scripts/cookies.json",
    "delay": 0,
    "removeSelectors": [...debugRemoveSelectors],
    "misMatchThreshold" : 0.1,
    "postInteractionWait": 0,
    "selectorExpansion": true,
    "expect": 0,
    "requireSameDimensions": true
  },
  "scenarios": [
    {
      "label": "Home",
      "url": `${BASE_URL}/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "hideSelectors": [],
      "removeSelectors": [
        ".event-card__image",
        ".event-card__location",
        ".event-card__day",
        ".event-card__time",
        ".rich-text-description",
        ".featured-event-card__image",
        ".featured-event-card__location",
        ".featured-event-card__date-copy",
        ".featured-event-card__title",
        ".featured-event-card__day",
        ".featured-event-card__time"
      ],
      "hoverSelector": "",
      "clickSelector": "",
      "selectors": []
    },
    {
      "label": "Events list",
      "url": `${BASE_URL}/events/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "hideSelectors": [],
      "removeSelectors": [
        ".event-card-full-width__image",
        ".event-card-full-width__location",
        ".event-card-full-width__date-copy",
        ".event-card-full-width__title",
        ".event-card-full-width__day",
        ".event-card-full-width__time",
        ".rich-text-description"
      ],
      "hoverSelector": "",
      "clickSelector": "",
      "selectors": []
    },
    {
      "label": "Event detail",
      "url": `${BASE_URL}/events/la-novela-virgenes-y-toxicomanos-de-mario-mendoza/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "hideSelectors": [],
      "removeSelectors": [
        "gmp-map",
        ".featured-event-card__image",
        ".featured-event-card__location",
        ".featured-event-card__date-copy",
        ".featured-event-card__title",
        ".featured-event-card__day",
        ".featured-event-card__time",
        ".event-detail time",
        ".event-detail img"
      ],
      "hoverSelector": "",
      "clickSelector": "",
      "selectors": []
    },
    {
      "label": "Header",
      "url": `${BASE_URL}/`,
      "referenceUrl": "",
      "readyEvent": "",
      "readySelector": "",
      "hideSelectors": [],
      "removeSelectors": [],
      "hoverSelector": "",
      "clickSelector": "",
      "selectors": [".header"],
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
