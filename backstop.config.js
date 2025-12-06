/* eslint-env process module */

const isProd = process.argv.includes("--prod");

const BASE_URL = isProd
  ? "https://desparchado.co"
  : "http://localhost:8000";

const TEST_NAME_PREFIX = isProd ? "PROD" : "LOCAL";

const IGNORE_DEBUG_TOOLBAR = !isProd;
const debugRemoveSelectors = IGNORE_DEBUG_TOOLBAR
  ? ["#djDebugToolbar", ".djdt-hidden"]
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
    "delay": 300,
    "referenceUrl": "",
    "readyEvent": "",
    "readySelector": "",
    "removeSelectors": [...debugRemoveSelectors],
    "hoverSelector": "",
    "clickSelector": "",
    "selectors": [],
    "misMatchThreshold" : 0.1,
    "postInteractionWait": 0,
    "selectorExpansion": true,
    "expect": 0,
    "requireSameDimensions": true
  },
  "scenarios": [
    {
      "label": `${TEST_NAME_PREFIX} Home`,
      "url": `${BASE_URL}/`,
      "hideSelectors": [
        ".event-card__location",
        ".event-card__day",
        ".event-card__time",
        ".rich-text-description",
        ".featured-event-card__location",
        ".featured-event-card__date-copy",
        ".featured-event-card__title",
        ".featured-event-card__day",
        ".featured-event-card__time"
      ],
      "removeSelectors": [
        ...debugRemoveSelectors,
        ".event-card__image",
        ".featured-event-card__image"
      ],
    },
    {
      "label": `${TEST_NAME_PREFIX} Events list`,
      "url": `${BASE_URL}/events/`,
      "hideSelectors": [
        ".event-card-full-width__location",
        ".event-card-full-width__date-copy",
        ".event-card-full-width__title",
        ".event-card-full-width__day",
        ".event-card-full-width__time",
        ".rich-text-description"
      ],
      "removeSelectors": [
        ...debugRemoveSelectors,
        ".event-card-full-width__image"
      ]
    },
    {
      "label": `${TEST_NAME_PREFIX} Event detail`,
      "url": `${BASE_URL}/events/la-novela-virgenes-y-toxicomanos-de-mario-mendoza/`,
      "hideSelectors": [
        ".featured-event-card__location",
        ".featured-event-card__date-copy",
        ".featured-event-card__title",
        ".featured-event-card__day",
        ".featured-event-card__time"
      ],
      "removeSelectors": [
        ...debugRemoveSelectors,
        "gmp-map",
        ".featured-event-card__image"
      ]
    },
    {
      "label": `${TEST_NAME_PREFIX} Header`,
      "url": `${BASE_URL}/`,
      "hideSelectors": [],
      "removeSelectors": [
        ...debugRemoveSelectors
      ],
      "selectors": [".header"],
    },
    {
      "label": `${TEST_NAME_PREFIX} Footer`,
      "url": `${BASE_URL}/`,
      "hideSelectors": [],
      "removeSelectors": [
        ...debugRemoveSelectors
      ],
      "selectors": [".footer"],
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
