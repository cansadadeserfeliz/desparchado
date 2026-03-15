/**
 * @file datetime_widget.js
 *
 * Self-contained datetime picker for the Desparchado event creation form.
 *
 * Attaches to every `.datetime-widget__input` element found in the page.
 * Shows a floating panel with:
 *   - A month/year calendar grid for date selection.
 *   - Two number inputs for hour (00-23) and minute (00-59).
 *   - A "Listo" confirm button that writes YYYY-MM-DD HH:MM into the input.
 *
 * No external dependencies. Requires the companion CSS file.
 *
 * Keyboard:
 *   Escape  — close panel without confirming.
 *   Enter   — confirm selection when focus is on the Listo button.
 */

(function () {
  'use strict';

  // ─── Constants ────────────────────────────────────────────────────────────

  const MONTH_NAMES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
  ];

  // Spanish week starts on Monday. Labels ordered Mo→Su.
  const DAY_LABELS = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];

  /**
   * Index into a Monday-based week grid (0 = Monday … 6 = Sunday).
   * JS Date.getDay() returns 0 = Sunday … 6 = Saturday.
   *
   * @param {number} jsDayIndex - Value from Date.prototype.getDay()
   * @returns {number} 0-based index in the Monday-first grid
   */
  function mondayBasedIndex(jsDayIndex) {
    return (jsDayIndex + 6) % 7;
  }

  /**
   * Zero-pad a number to at least two digits.
   *
   * @param {number} n
   * @returns {string}
   */
  function pad2(n) {
    return String(n).padStart(2, '0');
  }

  /**
   * Format a Date as "YYYY-MM-DD HH:MM".
   *
   * @param {Date} date
   * @param {number} hours   - 0-23
   * @param {number} minutes - 0-59
   * @returns {string}
   */
  function formatDatetime(date, hours, minutes) {
    const y = date.getFullYear();
    const m = pad2(date.getMonth() + 1);
    const d = pad2(date.getDate());
    return `${y}-${m}-${d} ${pad2(hours)}:${pad2(minutes)}`;
  }

  /**
   * Parse a "YYYY-MM-DD HH:MM" string into its parts.
   * Returns null if the string does not match the expected format.
   *
   * @param {string} value
   * @returns {{ year: number, month: number, day: number, hours: number, minutes: number } | null}
   */
  function parseDatetime(value) {
    const match = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$/.exec(value?.trim() ?? '');
    if (!match) return null;
    return {
      year: parseInt(match[1], 10),
      month: parseInt(match[2], 10) - 1, // 0-based
      day: parseInt(match[3], 10),
      hours: parseInt(match[4], 10),
      minutes: parseInt(match[5], 10),
    };
  }

  // ─── Panel builder ─────────────────────────────────────────────────────────

  /**
   * Build and return the floating panel DOM element for one picker instance.
   * The panel is appended to document.body so it can overflow any clipping
   * ancestors.
   *
   * @param {object} state - Mutable state object; panel sub-elements are
   *                         stored back into it.
   * @returns {HTMLElement}
   */
  function buildPanel(state) {
    const panel = document.createElement('div');
    panel.className = 'datetime-widget__panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-modal', 'false');
    panel.setAttribute('aria-label', 'Seleccionar fecha y hora');

    // ── Calendar ─────────────────────────────────────────────────────────────
    const calendar = document.createElement('div');
    calendar.className = 'datetime-widget__calendar';

    const calHeader = document.createElement('div');
    calHeader.className = 'datetime-widget__cal-header';

    const prevBtn = document.createElement('button');
    prevBtn.type = 'button';
    prevBtn.className = 'datetime-widget__cal-nav';
    prevBtn.setAttribute('aria-label', 'Mes anterior');
    prevBtn.textContent = '‹';

    const calTitle = document.createElement('span');
    calTitle.className = 'datetime-widget__cal-title';

    const nextBtn = document.createElement('button');
    nextBtn.type = 'button';
    nextBtn.className = 'datetime-widget__cal-nav';
    nextBtn.setAttribute('aria-label', 'Mes siguiente');
    nextBtn.textContent = '›';

    calHeader.appendChild(prevBtn);
    calHeader.appendChild(calTitle);
    calHeader.appendChild(nextBtn);

    const calGrid = document.createElement('div');
    calGrid.className = 'datetime-widget__cal-grid';
    calGrid.setAttribute('role', 'grid');

    DAY_LABELS.forEach((label) => {
      const dow = document.createElement('div');
      dow.className = 'datetime-widget__cal-dow';
      dow.setAttribute('role', 'columnheader');
      dow.setAttribute('aria-label', label);
      dow.textContent = label;
      calGrid.appendChild(dow);
    });

    calendar.appendChild(calHeader);
    calendar.appendChild(calGrid);

    // ── Time row ──────────────────────────────────────────────────────────────
    const timeRow = document.createElement('div');
    timeRow.className = 'datetime-widget__time';

    const timeLabel = document.createElement('span');
    timeLabel.className = 'datetime-widget__time-label';
    timeLabel.textContent = 'Hora';

    const hourInput = document.createElement('input');
    hourInput.type = 'number';
    hourInput.className = 'datetime-widget__time-input';
    hourInput.min = '0';
    hourInput.max = '23';
    hourInput.value = '00';
    hourInput.setAttribute('aria-label', 'Hora (00-23)');

    const timeSep = document.createElement('span');
    timeSep.className = 'datetime-widget__time-sep';
    timeSep.textContent = ':';

    const minInput = document.createElement('input');
    minInput.type = 'number';
    minInput.className = 'datetime-widget__time-input';
    minInput.min = '0';
    minInput.max = '59';
    minInput.value = '00';
    minInput.setAttribute('aria-label', 'Minutos (00-59)');

    timeRow.appendChild(timeLabel);
    timeRow.appendChild(hourInput);
    timeRow.appendChild(timeSep);
    timeRow.appendChild(minInput);

    // ── Footer ────────────────────────────────────────────────────────────────
    const footer = document.createElement('div');
    footer.className = 'datetime-widget__footer';

    const confirmBtn = document.createElement('button');
    confirmBtn.type = 'button';
    confirmBtn.className = 'datetime-widget__confirm';
    confirmBtn.textContent = 'Listo';

    footer.appendChild(confirmBtn);

    panel.appendChild(calendar);
    panel.appendChild(timeRow);
    panel.appendChild(footer);

    document.body.appendChild(panel);

    // Store sub-element references back into state
    state.panel = panel;
    state.calGrid = calGrid;
    state.calTitle = calTitle;
    state.hourInput = hourInput;
    state.minInput = minInput;

    // ── Internal event wiring ─────────────────────────────────────────────────
    prevBtn.addEventListener('click', () => {
      state.viewMonth -= 1;
      if (state.viewMonth < 0) {
        state.viewMonth = 11;
        state.viewYear -= 1;
      }
      renderCalendar(state);
    });

    nextBtn.addEventListener('click', () => {
      state.viewMonth += 1;
      if (state.viewMonth > 11) {
        state.viewMonth = 0;
        state.viewYear += 1;
      }
      renderCalendar(state);
    });

    confirmBtn.addEventListener('click', () => confirmSelection(state));

    hourInput.addEventListener('change', () => clampTimeInput(hourInput, 0, 23));
    minInput.addEventListener('change', () => clampTimeInput(minInput, 0, 59));

    panel.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        closePanel(state);
      }
    });

    // Prevent outside-click handler from firing when clicking inside the panel
    panel.addEventListener('mousedown', (e) => e.stopPropagation());

    return panel;
  }

  /**
   * Clamp the value of a time number input to [min, max].
   *
   * @param {HTMLInputElement} input
   * @param {number} min
   * @param {number} max
   */
  function clampTimeInput(input, min, max) {
    const raw = parseInt(input.value, 10);
    input.value = isNaN(raw) ? pad2(min) : pad2(Math.min(max, Math.max(min, raw)));
  }

  // ─── Calendar rendering ────────────────────────────────────────────────────

  /**
   * Re-render day cells inside state.calGrid for state.viewYear / state.viewMonth.
   * The 7 day-of-week header cells are preserved; only day buttons are replaced.
   *
   * @param {object} state
   */
  function renderCalendar(state) {
    const { calGrid, calTitle, viewYear, viewMonth, selected } = state;

    calTitle.textContent = `${MONTH_NAMES[viewMonth]} ${viewYear}`;

    const DOW_CELL_COUNT = 7;
    while (calGrid.children.length > DOW_CELL_COUNT) {
      calGrid.removeChild(calGrid.lastChild);
    }

    const today = new Date();
    const firstDay = new Date(viewYear, viewMonth, 1);
    const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();

    const startOffset = mondayBasedIndex(firstDay.getDay());
    for (let i = 0; i < startOffset; i++) {
      const empty = document.createElement('div');
      empty.className = 'datetime-widget__cal-day datetime-widget__cal-day--empty';
      empty.setAttribute('aria-hidden', 'true');
      calGrid.appendChild(empty);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'datetime-widget__cal-day';
      btn.textContent = String(day);
      btn.setAttribute('aria-label', `${day} de ${MONTH_NAMES[viewMonth]} de ${viewYear}`);

      const isToday = (
        viewYear === today.getFullYear() &&
        viewMonth === today.getMonth() &&
        day === today.getDate()
      );
      if (isToday) {
        btn.classList.add('datetime-widget__cal-day--today');
        btn.setAttribute('aria-current', 'date');
      }

      const isSelected = (
        selected !== null &&
        viewYear === selected.getFullYear() &&
        viewMonth === selected.getMonth() &&
        day === selected.getDate()
      );
      btn.classList.toggle('datetime-widget__cal-day--selected', isSelected);
      btn.setAttribute('aria-pressed', String(isSelected));

      btn.addEventListener('click', () => {
        state.selected = new Date(viewYear, viewMonth, day);
        renderCalendar(state);
      });

      calGrid.appendChild(btn);
    }
  }

  // ─── Panel open / close / confirm ─────────────────────────────────────────

  function positionPanel(state) {
    const rect = state.input.getBoundingClientRect();
    state.panel.style.top = `${rect.bottom + window.scrollY + 4}px`;
    state.panel.style.left = `${rect.left + window.scrollX}px`;
  }

  function openPanel(state) {
    positionPanel(state);
    state.panel.classList.add('datetime-widget__panel--open');
    state.input.setAttribute('aria-expanded', 'true');
  }

  function closePanel(state) {
    state.panel.classList.remove('datetime-widget__panel--open');
    state.input.setAttribute('aria-expanded', 'false');
  }

  function confirmSelection(state) {
    const date = state.selected || new Date();
    const hours = parseInt(state.hourInput.value, 10) || 0;
    const minutes = parseInt(state.minInput.value, 10) || 0;
    state.input.value = formatDatetime(date, hours, minutes);
    state.input.dispatchEvent(new Event('change', { bubbles: true }));
    closePanel(state);
    state.input.focus();
  }

  // ─── Initialise one input ──────────────────────────────────────────────────

  /**
   * Attach the datetime picker to a single `.datetime-widget__input` element.
   *
   * @param {HTMLInputElement} input
   */
  function initInput(input) {
    const now = new Date();
    const state = {
      input,
      panel: null,
      calGrid: null,
      calTitle: null,
      hourInput: null,
      minInput: null,
      selected: null,
      viewYear: now.getFullYear(),
      viewMonth: now.getMonth(),
    };

    const parsed = parseDatetime(input.value);
    if (parsed !== null) {
      state.selected = new Date(parsed.year, parsed.month, parsed.day);
      state.viewYear = parsed.year;
      state.viewMonth = parsed.month;
    }

    buildPanel(state);
    renderCalendar(state);

    if (parsed !== null) {
      state.hourInput.value = pad2(parsed.hours);
      state.minInput.value = pad2(parsed.minutes);
    }

    input.setAttribute('aria-haspopup', 'dialog');
    input.setAttribute('aria-expanded', 'false');

    input.addEventListener('focus', () => openPanel(state));

    input.addEventListener('click', () => {
      if (!state.panel.classList.contains('datetime-widget__panel--open')) {
        openPanel(state);
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        closePanel(state);
      }
    });

    const onResize = () => {
      if (state.panel.classList.contains('datetime-widget__panel--open')) {
        positionPanel(state);
      }
    };
    window.addEventListener('resize', onResize);

    const observer = new MutationObserver(() => {
      if (!document.body.contains(input)) {
        window.removeEventListener('resize', onResize);
        if (state.panel.parentNode) {
          state.panel.parentNode.removeChild(state.panel);
        }
        observer.disconnect();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // ─── Outside-click handler (document-level) ───────────────────────────────

  // Capture phase: stop propagation for clicks on the input itself so the
  // bubble-phase closer below does not immediately close a just-opened panel.
  document.addEventListener('mousedown', (e) => {
    if (e.target.classList.contains('datetime-widget__input')) {
      e.stopPropagation();
    }
  }, true);

  document.addEventListener('mousedown', () => {
    document.querySelectorAll('.datetime-widget__panel--open').forEach((panel) => {
      panel.classList.remove('datetime-widget__panel--open');
    });
    document.querySelectorAll('.datetime-widget__input[aria-expanded="true"]').forEach((inp) => {
      inp.setAttribute('aria-expanded', 'false');
    });
  });

  // ─── Bootstrap ────────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.datetime-widget__input').forEach(initInput);
  });

})();