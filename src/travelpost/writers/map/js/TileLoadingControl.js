if (typeof L.Travel === "undefined") {
  L.Travel = {};
}

L.Travel.TileLoadingControl = L.Control.extend({
  initialize: function (options) {
    L.Control.prototype.initialize.call(this, options);
    this._counter = 0;
  },

  onAdd: function (map) {
    map.eachLayer(this._attach, this);
    map.on("layeradd", this._attach_event, this);

    this._div = L.DomUtil.create("div", "tile-loading-control");
    this._div.dataset.ready = false;
    return this._div;
  },

  onRemove: function (map) {
    map.eachLayer(this._detach, this);
    map.off("layeradd", this._attach_event, this);
  },

  _attach: function (layer) {
    if (layer instanceof L.TileLayer) {
      layer.on("loading", this._onLoading, this);
      layer.on("load", this._onLoad, this);
    }
  },

  _attach_event: function (e) {
    this._attach(e.layer);
  },

  _detach: function (layer) {
    if (layer instanceof L.TileLayer) {
      layer.off("loading", this._onLoading, this);
      layer.off("load", this._onLoad, this);
    }
  },

  _onLoading: function () {
    this._counter += 1;
    if (this._div.dataset.ready) {
      this._div.dataset.ready = false;
    }
  },

  _onLoad: function () {
    this._counter -= 1;
    if (this._counter <= 0) {
      this._div.dataset.ready = true;
    }
  },
});

L.Travel.tileLoadingControl = function (options) {
  return new L.Travel.TileLoadingControl(options);
};
