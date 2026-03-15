// Extracted from django-map-widgets v0.5.1 (https://github.com/erdem/django-map-widgets)
// Changes applied:
//   - googleMapWidgetsCallback: removed window.addEventListener("load", ...) wrapper;
//     now iterates mapWidgets.googleMapCallbacks immediately so initialization happens
//     as soon as the Google Maps API calls the callback, avoiding a load-event race.
mapWidgets = {};

// Array to store callback functions for Google Maps widget Classes
// These functions will be executed when the Google Maps API finishes loading
mapWidgets.googleMapCallbacks = []

// First, try to use the jQuery instance from Django Admin (if available)
// If Django Admin jQuery is not available, use the global jQuery instance
if (typeof django !== "undefined" && django.jQuery) {
    mapWidgets.jQuery = django.jQuery.noConflict();
} else {
    mapWidgets.jQuery = jQuery.noConflict();
}


// This callback function execute by GoogleMap JS.
function googleMapWidgetsCallback() {
    for (let index = 0; index < mapWidgets.googleMapCallbacks.length; index++) {
        const widgetCallback = mapWidgets.googleMapCallbacks[index];
        new widgetCallback.class(widgetCallback.options);
    }
}


(function ($) {

    let initializing = false, fnTest = /xyz/.test(function () {
        xyz;
    }) ? /\bSuper\b/ : /.*/;

    $.Class = function () {

    };

    $.Class.extend = function (prop) {
        const Super = this.prototype;
        initializing = true;
        let prototype = new this();
        initializing = false;

        for (let name in prop) {
            prototype[name] = typeof prop[name] == "function" && typeof Super[name] == "function" && fnTest.test(prop[name]) ? (function (name, fn) {
                return function () {
                    let tmp = this.Super;
                    this.Super = Super[name];
                    const ret = fn.apply(this, arguments);
                    this.Super = tmp;
                    return ret;
                };
            })(name, prop[name]) : prop[name];
        }

        function Class() {
            if (!initializing && this.init) {
                this.init.apply(this, arguments);
            }
        }

        Class.prototype = prototype;

        Class.constructor = Class;

        Class.extend = arguments.callee;

        return Class;
    };

    if (typeof Function.prototype.bind === 'undefined') {

        Function.prototype.bind = function (obj) {
            const method = this;

            const tmp = function () {
                return method.apply(obj, arguments);
            };

            return tmp;
        };

    }

    if (!Array.prototype.indexOf) {
        Array.prototype.indexOf = function (obj) {
            for (let i = 0; i < this.length; i++) {
                if (this[i] === obj) {
                    return i;
                }
            }

            return -1;
        };
    }

})(mapWidgets.jQuery);