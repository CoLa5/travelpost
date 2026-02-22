if (typeof L.Travel === "undefined") {
  L.Travel = {};
}

L.Travel.POI_ICON_MAP = {
  airport: { icon: "plane-up", style: "solid" },
  busstation: { icon: "bus-simple", style: "solid" },
  campsite: { icon: "campground", style: "solid" },
  castle: { icon: "font-awesome", style: "solid" },
  cave: { icon: "cave", style: "solid" },
  // cementory: { icon: "", style: "solid" },
  church: { icon: "church", style: "solid" },
  city: { icon: "city", style: "solid" },
  fountain: { icon: "droplet", style: "solid" },
  harbour: { icon: "anchor", style: "solid" },
  hospital: { icon: "hospital", style: "solid" },
  hostel: { icon: "bed", style: "solid" },
  hotel: { icon: "h", style: "solid" },
  lake: { icon: "water", style: "solid" },
  // lighthouse: { icon: "", style: "solid" },
  // mine: { icon: "", style: "solid" }, // hammer + amboss
  monument: { icon: "monument", style: "solid" },
  mountain: { icon: "mountain", style: "solid" },
  mountain_pass: { icon: "mixer", style: "solid" },
  museum: { icon: "building-columns", style: "solid" },
  observation_tower: { icon: "tower-observation", style: "solid" },
  pass: { icon: "mixer", style: "solid" },
  peak: { icon: "mountain", style: "solid" },
  point_of_interest: { icon: "star", style: "solid" },
  port: { icon: "anchor", style: "solid" },
  refugee: { icon: "house", style: "solid" },
  store: { icon: "store", style: "solid" },
  trainstation: { icon: "train", style: "solid" },
  tree: { icon: "tree", style: "solid" },
  // waterfall: { icon: "", style: "solid" },
  water_point: { icon: "droplet", style: "solid" },
  winery: { icon: "wine-glas", style: "solid" },
  unknown: { icon: "location-dot", style: "solid" },
  viewpoint: { icon: "binocular", style: "solid" },
  volcano: { icon: "volcano", style: "solid" },
};

L.Travel.PointOfInterest = L.Layer.extend({
  options: {
    iconOptions: {
      iconPadding: 0,
      iconShape: "square",
      iconSize: 16,
    },
    textOptions: {
      color: "black",
      fontSize: "11pt",
      padding: "1pt 0 0pt",
    },
    outlineStroke: "0.3em white",
  },

  initialize: function (latlng, symbol, name, options) {
    L.Util.setOptions(this, options);
    this.options.iconOptions = L.Util.extend(
      {},
      L.Travel.PointOfInterest.prototype.options.iconOptions,
      options.iconOptions,
    );
    this.options.iconOptions.outlineStroke = this.options.outlineStroke;
    this.options.textOptions = L.Util.extend(
      {},
      L.Travel.PointOfInterest.prototype.options.textOptions,
      options.textOptions,
    );
    this.options.textOptions.outlineStroke = this.options.outlineStroke;

    latlng = L.latLng(latlng);

    symbol = String(symbol ?? "unknown").toLowerCase();
    const iconDef = L.Travel.POI_ICON_MAP[symbol];
    if (!iconDef) {
      throw Error("missing symbol definition: " + symbol);
    }

    let texts = String(name).split("<br>", 2);
    if (texts.length == 1) {
      texts = ["", texts[0]];
    }

    this._marker = L.marker(latlng, {
      icon: L.Travel.faIcon({
        ...this.options.iconOptions,
        icon: iconDef.icon,
        iconStyle: iconDef.style,
      }),
    });
    const iconSize = this._marker.options.icon.options.iconSize[1];
    this._header = L.tooltip(latlng, {
      className: "poi-text",
      content: this._createTextElement(texts[0], this.options.textOptions),
      direction: "top",
      offset: [0, -iconSize / 2],
      opacity: 1.0,
      permanent: true,
      sticky: false,
    });
    this._trailer = L.tooltip(latlng, {
      className: "poi-text",
      content: this._createTextElement(texts[1], this.options.textOptions),
      direction: "bottom",
      offset: [0, iconSize / 2],
      opacity: 1.0,
      permanent: true,
      sticky: false,
    });
    this._group = L.featureGroup([
      this._marker,
      this._header,
      this._trailer,
    ]).bindTooltip(name || L.Travel._titleCase(symbol), { sticky: true });
  },

  onAdd: function (map) {
    this._group.addTo(map);
  },

  onRemove: function () {
    this._group.remove();
  },

  // @method getLatLng: LatLng
  // Returns the current geographical position of the marker.
  getLatLng: function () {
    return this._marker.getLatlng();
  },

  // @method setLatLng(latlng: LatLng): this
  // Changes the marker position to the given point.
  setLatLng: function (latlng) {
    this._marker.setLatLng(latlng);
    this._header.setLatLng(latlng);
    this._trailer.setLatLng(latlng);
  },

  // @method getName: String
  // Returns the current name of the marker.
  getName: function () {
    return this._name;
  },

  // @method setName(name: String): this
  // Changes the marker name to the given name.
  setName: function (name) {
    let texts = String(name).split("\n", 2);
    if (texts.length == 1) {
      texts = ("", texts[0]);
    }

    let p = this._header.getContent().querySelector(":scope > p");
    p.dataset.text = texts[0];
    p.textContent = texts[0];

    p = this._trailer.getContent().querySelector(":scope > p");
    p.dataset.text = texts[1];
    p.textContent = texts[1];
  },

  _createTextElement: function (text, options) {
    const p = document.createElement("p");
    p.textContent = text;
    if (options.color) p.style.color = options.color;
    if (options.fontSize) p.style.fontSize = options.fontSize;
    if (options.padding) p.style.padding = options.padding;
    if (options.outlineStroke && options.outlineStroke != "none") {
      p.dataset.text = text;
      p.style.setProperty("--text-stroke", options.outlineStroke);
    }
    return p;
  },
});

L.Travel.pointOfInterest = function (latlng, symbol, name, options) {
  return new L.Travel.PointOfInterest(latlng, symbol, name, options);
};
