// Extracted from django-map-widgets v0.5.1 (https://github.com/erdem/django-map-widgets)
// Reason: google.maps.places.Autocomplete is deprecated for new customers as of March 2025.
// Changes applied:
//   - initializePlaceAutocomplete: replaced Autocomplete with PlaceAutocompleteElement,
//     loaded via google.maps.importLibrary("places") to ensure the new Places API is available;
//     mapped componentRestrictions.country to includedRegionCodes for the new API.
//   - handleAutoCompletePlaceChange: replaced place_changed/getPlace() with the gmp-select
//     event; place is obtained via event.placePrediction.toPlace() + fetchFields().
//   - addMarkerToMap: switched from AdvancedMarkerElement (requires a Cloud Console Map ID)
//     to google.maps.Marker which works without a Map ID.
//   - serializeMarkerToGeoJSON / fitBoundMarker: updated to use getPosition() instead of
//     .position property (legacy Marker API).
//   - handleAutoCompleteInputKeyDown: removed (PlaceAutocompleteElement handles Enter internally).
(function ($) {
    DjangoGooglePointFieldWidget = DjangoMapWidgetBase.extend({

        initializeMap: async function () {

            // Redefine setMapOptions inside initializeMap to create a new closure for each instance
            const setMapOptions = async () => {
                let mapInitializeOptions = {
                    zoomControlOptions: {
                        position: google.maps.ControlPosition.RIGHT
                    },
                };

                mapInitializeOptions = $.extend({}, mapInitializeOptions, this.mapOptions);

                let mapCenter = mapInitializeOptions.center;
                if (!(mapCenter instanceof google.maps.LatLng) && Array.isArray(mapCenter)) {
                    mapCenter = new google.maps.LatLng(mapCenter[0], mapCenter[1]);
                }

                if (this.mapCenterLocationName) {
                    try {
                        const response = await new Promise((resolve, reject) => {
                            this.geocoder.geocode({'address': this.mapCenterLocationName}, (results, status) => {
                                if (status === google.maps.GeocoderStatus.OK) {
                                    resolve(results);
                                } else {
                                    reject(status);
                                }
                            });
                        });
                        const geo_location = response[0].geometry.location;
                        mapCenter = new google.maps.LatLng(geo_location.lat(), geo_location.lng());
                    } catch (error) {
                        console.error('Geocode lookup failed for `mapCenterLocationName` option:', error);
                    }
                }

                mapInitializeOptions["center"] = mapCenter;

                return mapInitializeOptions;
            };

            // Rest of the initializeMap function
            this.geocoder = new google.maps.Geocoder();
            const mapOptions = await setMapOptions();

            this.map = new google.maps.Map(this.mapElement, mapOptions);

            if (!$.isEmptyObject(this.djangoGeoJSONValue)) {
                this.addMarkerToMap(this.djangoGeoJSONValue.lat, this.djangoGeoJSONValue.lng);
                this.updateDjangoInput();
                this.fitBoundMarker();
            }
            await this.initializePlaceAutocomplete();
        },

        initializePlaceAutocomplete: async function () {
            const { PlaceAutocompleteElement } = await google.maps.importLibrary("places");

            const autocompleteOptions = {};
            const opts = this.GooglePlaceAutocompleteOptions || {};
            if (opts.componentRestrictions && opts.componentRestrictions.country) {
                const country = opts.componentRestrictions.country;
                autocompleteOptions.includedRegionCodes = Array.isArray(country) ? country : [country];
            }
            if (opts.types) {
                autocompleteOptions.types = opts.types;
            }

            const autocompleteElement = new PlaceAutocompleteElement(autocompleteOptions);
            const existingInput = this.addressAutoCompleteInput;
            autocompleteElement.id = existingInput.id;
            autocompleteElement.className = existingInput.className;
            existingInput.parentNode.replaceChild(autocompleteElement, existingInput);
            this.addressAutoCompleteInput = autocompleteElement;

            this.autocomplete = autocompleteElement;
            this.autocomplete.addEventListener('gmp-select', this.handleAutoCompletePlaceChange.bind(this));
        },

        addMarkerToMap: function (lat, lng) {
            this.removeMarker();
            const marker_position = {lat: parseFloat(lat), lng: parseFloat(lng)};
            this.marker = new google.maps.Marker({
                map: this.map,
                position: marker_position,
                draggable: true
            });
            this.marker.addListener("dragend", this.dragMarker.bind(this));
        },

        serializeMarkerToGeoJSON: function () {
            if (this.marker) {
                const position = this.marker.getPosition();
                return {
                    type: "Point",
                    coordinates: [position.lng(), position.lat()]
                };
            }
        },

        fitBoundMarker: function () {
            const bounds = new google.maps.LatLngBounds();
            bounds.extend(this.marker.getPosition());
            this.map.fitBounds(bounds);
            if (this.markerFitZoom && this.isInt(this.markerFitZoom)) {
                const markerFitZoom = parseInt(this.markerFitZoom);
                const listener = google.maps.event.addListener(this.map, "idle", function () {
                    if (this.getZoom() > markerFitZoom) {
                        this.setZoom(markerFitZoom)
                    }
                    google.maps.event.removeListener(listener);
                });
            }
        },

        removeMarker: function (e) {
            if (this.marker) {
                this.marker.setMap(null);
            }
            this.marker = null;
        },

        dragMarker: function (e) {
            this.addMarkerToMap(e.latLng.lat(), e.latLng.lng())
            this.updateDjangoInput()
        },

        handleAutoCompletePlaceChange: async function (event) {
            const place = event.placePrediction.toPlace();
            try {
                await place.fetchFields({fields: ['location', 'formattedAddress']});
            } catch (error) {
                console.error('GoogleMapPointFieldWidget: fetchFields failed', error);
                return;
            }
            if (!place.location) {
                return;
            }
            this.addMarkerToMap(place.location.lat(), place.location.lng());
            this.updateDjangoInput(place);
            this.fitBoundMarker();
        },

        handleAddMarkerBtnClick: function (e) {
            $(this.mapElement).toggleClass("click");
            this.addMarkerBtn.toggleClass("active");
            if ($(this.addMarkerBtn).hasClass("active")) {
                this.map.addListener("click", this.handleMapClick.bind(this));
            } else {
                google.maps.event.clearListeners(this.map, 'click');
            }
        },

        handleMapClick: function (e) {
            google.maps.event.clearListeners(this.map, 'click');
            $(this.mapElement).removeClass("click");
            this.addMarkerBtn.removeClass("active");
            this.addMarkerToMap(e.latLng.lat(), e.latLng.lng())
            this.updateDjangoInput()
        },

        callPlaceTriggerHandler: function (lat, lng, place) {
            if (place === undefined) {
                var latlng = {lat: parseFloat(lat), lng: parseFloat(lng)};
                this.geocoder.geocode({'location': latlng}, function (results, status) {
                    if (status === google.maps.GeocoderStatus.OK) {
                        var placeObj = results[0] || {};
                        $(this.addressAutoCompleteInput).val(placeObj.formatted_address || "");
                        $(document).trigger(this.placeChangedTriggerNameSpace,
                            [placeObj, lat, lng, this.wrapElemSelector, this.djangoInput]
                        );
                        if ($.isEmptyObject(this.djangoGeoJSONValue)) {
                            $(document).trigger(this.markerCreateTriggerNameSpace,
                                [placeObj, lat, lng, this.wrapElemSelector, this.djangoInput]
                            );
                        } else {
                            $(document).trigger(this.markerChangeTriggerNameSpace,
                                [placeObj, lat, lng, this.wrapElemSelector, this.djangoInput]
                            );
                        }
                    }
                }.bind(this));
            } else {  // user entered an address
                $(document).trigger(this.placeChangedTriggerNameSpace,
                    [place, lat, lng, this.wrapElemSelector, this.djangoInput]
                );
            }
        },
    });

})(mapWidgets.jQuery);