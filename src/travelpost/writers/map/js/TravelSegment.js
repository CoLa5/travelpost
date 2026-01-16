if (typeof L.Travel === "undefined") {
  L.Travel = {};
}

L.Travel.TRANSPORT_ICON_MAP = {
  barefoot: { icon: "shoe-prints", style: "solid" },
  walking: { icon: "person-walking", style: "solid" },
  hiking: { icon: "person-hiking", style: "solid" },
  running: { icon: "person-running", style: "solid" },
  bicycle: { icon: "person-bicycle", style: "solid" },
  flight: { icon: "plane", style: "solid" },
  car: { icon: "car-side", style: "solid" },
  bus: { icon: "bus-simple", style: "solid" },
  taxi: { icon: "taxi", style: "solid" },
  train: { icon: "train", style: "solid" },
  tram: { icon: "tram", style: "solid" },
  motorbike: { icon: "motorcycle", style: "solid" },
  "4x4": { icon: "truck-pickup", style: "solid" },
  tuk_tuk: { icon: "car", style: "solid" }, // TODO
  hitchhiking: { icon: "thumbs-up", style: "solid" },
  cable_car: { icon: "cable-car", style: "solid" },
  ferry: { icon: "ferry", style: "solid" },
  motorboat: { icon: "ship", style: "solid" },
  sailing: { icon: "sailboat", style: "solid" },
};

L.Travel._titleCase = function (str) {
  return str.toLowerCase().replace(/(?:^|\s)\w/g, function (match) {
    return match.toUpperCase();
  });
};

L.Travel.Segment = L.Polyline.extend({
  options: {
    color: "white",
    iconOptions: {
      iconShape: "rounded-square",
      iconSize: 24,
      backgroundColor: "#3388ff",
      borderColor: "white",
      borderWidth: 0,
      color: "white",
      fontSize: 16,
    },
    sizeFactor: 2,
    transportMarkerZIndexOffset: 0,
    weight: 3,
  },

  initialize: function (latlngs, transport, options) {
    L.Polyline.prototype.initialize.call(this, latlngs, options);
    this.options.iconOptions = L.Util.extend(
      {},
      L.Travel.Segment.prototype.options.iconOptions,
      this.options.iconOptions,
    );
    this._center = null;
    this._transport = String(transport ?? "unknown").toLowerCase();
    this._transportMarker = null;
  },

  getTransport: function () {
    return this._transport;
  },

  onAdd: function () {
    if (this._center === null) {
      this._center = this.getCenter();
    }
    L.Polyline.prototype.onAdd.call(this);
  },

  onRemove: function () {
    if (this._transportMarker !== null) {
      this._map.removeLayer(this._transportMarker);
      this._transportMarker = null;
    }
    L.Polyline.prototype.onRemove.call(this);
  },

  _setLatLngs: function (latlngs) {
    L.Polyline.prototype._setLatLngs.call(this, latlngs);
    if (this._map) {
      this._center = this.getCenter();
    }
  },

  _update: function () {
    L.Polyline.prototype._update.call(this);
    this._updateTransportIcon();
  },

  _updateTransportIcon: function () {
    if (!this._map || this._transport == "unknown") return;

    const iconDef = L.Travel.TRANSPORT_ICON_MAP[this._transport];
    if (!iconDef) {
      console.warn("missing transport definition: " + this._transport);
      return;
    }

    const bounds = this._renderer._bounds,
      size = this._pxBounds.getSize(),
      sizeLim = this.options.sizeFactor * this.options.iconOptions.iconSize,
      showMarker =
        this._pxBounds &&
        this._pxBounds.intersects(bounds) &&
        (size.x > sizeLim || size.y > sizeLim);

    if (this._transportMarker !== null && !showMarker) {
      this._map.removeLayer(this._transportMarker);
      this._transportMarker = null;
      return;
    }
    if (this._transportMarker === null && showMarker) {
      this._transportMarker = L.marker(this._center, {
        icon: L.Travel.faIcon({
          icon: iconDef.icon,
          iconStyle: iconDef.style,
          ...this.options.iconOptions,
        }),
        zIndexOffset: this.options.transportMarkerZIndexOffset,
      }).addTo(this._map);
      this._transportMarker.bindTooltip(L.Travel._titleCase(this._transport));
    }
  },
});

L.Travel.segment = function (latlngs, transport, options) {
  return new L.Travel.Segment(latlngs, transport, options);
};
