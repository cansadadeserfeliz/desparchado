/**
 * initLeafletPicker — self-contained Leaflet map picker for a Django PointField.
 *
 * Initialises a Leaflet map inside the element identified by `mapId` and wires
 * up all toolbar buttons and the address search input.  When the user places or
 * moves a marker the selected coordinates are serialised as a GeoJSON Point
 * string and written into the hidden textarea identified by `djangoInputId`,
 * which is the value read by Django's PointField on form submission.
 *
 * @param {string} mapId          - ID of the map container div.
 * @param {string} addressInputId - ID of the address search text input.
 * @param {string} djangoInputId  - ID of the hidden textarea consumed by Django.
 * @param {string} wrapId         - ID of the outer wrapper div (.mw-wrap).
 * @param {object|null} fieldValue - Saved point as {lat, lng, ...} or null.
 * @param {object} options         - Map options: {zoom, center, markerFitZoom}.
 */
window.initLeafletPicker = function initLeafletPicker(
    mapId, addressInputId, djangoInputId, wrapId, fieldValue, options
) {
    var map = L.map(mapId, { scrollWheelZoom: false });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    map.setView(options.center || [4.65, -74.08], options.zoom || 5);

    var marker = null;
    var clickModeActive = false;

    var wrap = document.getElementById(wrapId);

    // ── helpers ──────────────────────────────────────────────────────────────

    function updateDjangoInput(latlng) {
        var input = document.getElementById(djangoInputId);
        if (!input) { return; }
        input.value = JSON.stringify({
            type: 'Point',
            coordinates: [latlng.lng, latlng.lat]
        });

        // sync coordinate overlay inputs
        var latInput = wrap.querySelector('.mw-overlay-latitude');
        var lngInput = wrap.querySelector('.mw-overlay-longitude');
        if (latInput) { latInput.value = latlng.lat; }
        if (lngInput) { lngInput.value = latlng.lng; }

        // enable delete button
        var deleteBtn = wrap.querySelector('.mw-btn-delete');
        if (deleteBtn) {
            deleteBtn.classList.remove('mw-btn-default', 'disabled');
            deleteBtn.classList.add('mw-btn-danger');
        }
    }

    function clearDjangoInput() {
        var input = document.getElementById(djangoInputId);
        if (input) { input.value = ''; }

        var latInput = wrap.querySelector('.mw-overlay-latitude');
        var lngInput = wrap.querySelector('.mw-overlay-longitude');
        if (latInput) { latInput.value = ''; }
        if (lngInput) { lngInput.value = ''; }

        // disable delete button
        var deleteBtn = wrap.querySelector('.mw-btn-delete');
        if (deleteBtn) {
            deleteBtn.classList.remove('mw-btn-danger');
            deleteBtn.classList.add('mw-btn-default', 'disabled');
        }
    }

    function placeMarker(latlng) {
        if (marker) {
            marker.setLatLng(latlng);
        } else {
            marker = L.marker(latlng, { draggable: true }).addTo(map);
            marker.on('dragend', function () {
                updateDjangoInput(marker.getLatLng());
            });
        }
        updateDjangoInput(latlng);
    }

    function removeMarker() {
        if (marker) {
            map.removeLayer(marker);
            marker = null;
        }
        clearDjangoInput();
    }

    // ── initial marker ───────────────────────────────────────────────────────

    if (fieldValue && fieldValue.lat != null && fieldValue.lng != null) {
        var initialLatLng = L.latLng(fieldValue.lat, fieldValue.lng);
        placeMarker(initialLatLng);
        map.setView(initialLatLng, options.markerFitZoom || 15);
    }

    // ── "Mark on map" button ─────────────────────────────────────────────────

    var addMarkerBtn = wrap.querySelector('.mw-btn-add-marker');
    if (addMarkerBtn) {
        addMarkerBtn.addEventListener('click', function () {
            clickModeActive = !clickModeActive;
            var mapElem = document.getElementById(mapId);
            if (clickModeActive) {
                addMarkerBtn.classList.add('active');
                if (mapElem) { mapElem.classList.add('click'); }
            } else {
                addMarkerBtn.classList.remove('active');
                if (mapElem) { mapElem.classList.remove('click'); }
            }
        });
    }

    map.on('click', function (e) {
        if (!clickModeActive) { return; }
        placeMarker(e.latlng);
        clickModeActive = false;
        if (addMarkerBtn) { addMarkerBtn.classList.remove('active'); }
        var mapElem = document.getElementById(mapId);
        if (mapElem) { mapElem.classList.remove('click'); }
    });

    // ── "My location" button ─────────────────────────────────────────────────

    var myLocationBtn = wrap.querySelector('.mw-btn-my-location');
    if (myLocationBtn && navigator.geolocation) {
        myLocationBtn.addEventListener('click', function () {
            navigator.geolocation.getCurrentPosition(
                function (position) {
                    var latlng = L.latLng(
                        position.coords.latitude,
                        position.coords.longitude
                    );
                    placeMarker(latlng);
                    map.setView(latlng, options.markerFitZoom || 15);
                },
                function () {
                    alert('No se pudo obtener tu ubicación.');
                }
            );
        });
    }

    // ── Coordinates overlay ──────────────────────────────────────────────────

    var coordsBtn = wrap.querySelector('.mw-btn-coordinates');
    var coordsOverlay = wrap.querySelector('.mw-coordinates-overlay');

    if (coordsBtn && coordsOverlay) {
        coordsBtn.addEventListener('click', function () {
            coordsOverlay.classList.toggle('hide');
        });

        var coordsDoneBtn = wrap.querySelector('.mw-btn-coordinates-done');
        if (coordsDoneBtn) {
            coordsDoneBtn.addEventListener('click', function () {
                coordsOverlay.classList.add('hide');
            });
        }

        var latInput = wrap.querySelector('.mw-overlay-latitude');
        var lngInput = wrap.querySelector('.mw-overlay-longitude');

        function applyCoordinateInputs() {
            var lat = parseFloat(latInput ? latInput.value : '');
            var lng = parseFloat(lngInput ? lngInput.value : '');
            if (!isNaN(lat) && !isNaN(lng)) {
                var latlng = L.latLng(lat, lng);
                placeMarker(latlng);
                map.setView(latlng, options.markerFitZoom || 15);
            }
        }

        if (latInput) { latInput.addEventListener('change', applyCoordinateInputs); }
        if (lngInput) { lngInput.addEventListener('change', applyCoordinateInputs); }
    }

    // ── Delete button ────────────────────────────────────────────────────────

    var deleteBtn = wrap.querySelector('.mw-btn-delete');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function () {
            removeMarker();
        });
    }

    // ── Address search (Photon geocoding) ────────────────────────────────────

    var addressInput = document.getElementById(addressInputId);
    var photonResultsList = null;
    var debounceTimer = null;
    var activeController = null;

    function hidePhotonResults() {
        if (photonResultsList) {
            photonResultsList.style.display = 'none';
        }
    }

    function renderPhotonResults(features) {
        if (!photonResultsList) {
            photonResultsList = document.createElement('ul');
            photonResultsList.className = 'mw-photon-results';
            addressInput.parentNode.appendChild(photonResultsList);
        }

        photonResultsList.innerHTML = '';

        if (!features || features.length === 0) {
            hidePhotonResults();
            return;
        }

        features.forEach(function (feature) {
            var props = feature.properties || {};
            var label = props.name || '';
            var secondary = props.city || props.state || '';
            if (secondary) { label += ', ' + secondary; }

            var li = document.createElement('li');
            li.textContent = label;
            li.addEventListener('click', function () {
                var coords = feature.geometry && feature.geometry.coordinates;
                if (coords) {
                    var latlng = L.latLng(coords[1], coords[0]);
                    placeMarker(latlng);
                    map.setView(latlng, options.markerFitZoom || 15);
                }
                addressInput.value = label;
                hidePhotonResults();
            });
            photonResultsList.appendChild(li);
        });

        photonResultsList.style.display = 'block';
    }

    if (addressInput) {
        addressInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            if (activeController) {
                activeController.abort();
                activeController = null;
            }
            var q = addressInput.value.trim();
            if (q.length < 3) {
                hidePhotonResults();
                return;
            }
            debounceTimer = setTimeout(function () {
                activeController = new AbortController();
                var url = 'https://photon.komoot.io/api/?q=' +
                    encodeURIComponent(q) +
                    '&lang=es&limit=5&bbox=-81.7,-4.2,-66.9,12.5';
                fetch(url, { signal: activeController.signal })
                    .then(function (resp) { return resp.json(); })
                    .then(function (data) {
                        activeController = null;
                        renderPhotonResults(data.features || []);
                    })
                    .catch(function (err) {
                        if (err.name !== 'AbortError') {
                            hidePhotonResults();
                        }
                    });
            }, 300);
        });

        // hide results when clicking elsewhere
        document.addEventListener('click', function (e) {
            if (addressInput && !addressInput.contains(e.target) &&
                photonResultsList && !photonResultsList.contains(e.target)) {
                hidePhotonResults();
            }
        });
    }
};