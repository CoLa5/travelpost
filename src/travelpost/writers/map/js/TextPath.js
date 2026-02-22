L.SVG.TextPath = L.SVG.extend({
  _initPath: function (layer) {
    L.SVG.prototype._initPath.call(this, layer);

    if (layer.options.text) {
      this._initTextPath(layer);
    }
  },

  _addPath: function (layer) {
    L.SVG.prototype._addPath.call(this, layer);

    if (layer._text) {
      this._addTextPath(layer);
    }
  },

  _updatePath: function (layer) {
    L.SVG.prototype._updatePath.call(this, layer);

    if (layer._text) {
      this._updateTextPath(layer);
    }
  },

  _removePath: function (layer) {
    if (layer._text) {
      this._removeTextPath(layer);
    }

    L.SVG.prototype._removePath.call(this, layer);
  },

  _updateStyle: function (layer) {
    L.SVG.prototype._updateStyle.call(this, layer);

    if (layer._text) {
      this._updateTextStyle(layer);
    }
  },

  _initTextPath: function (layer) {
    const id = "path-" + L.Util.stamp(layer),
      text = L.SVG.create("text"),
      textPath = L.SVG.create("textPath");

    layer._path.setAttribute("id", id);

    L.DomUtil.addClass(text, "text-path");
    if (layer.options.textClassName) {
      L.DomUtil.addClass(text, layer.options.textClassName);
    }
    if (layer.options.interactive) {
      L.DomUtil.addClass(text, "leaflet-interactive");
    }

    layer._path.id = id;
    textPath.setAttributeNS(
      "http://www.w3.org/1999/xlink",
      "xlink:href",
      "#" + id,
    );
    textPath.textContent = String(layer.options.text);
    layer._textPath = textPath;

    text.appendChild(textPath);
    layer._text = text;

    this._updateTextStyle(layer);
  },

  _addTextPath: function (layer) {
    this._rootGroup.appendChild(layer._text);
    layer.addInteractiveTarget(layer._text);

    if (layer.options.interactive) {
      const events = [
        "click",
        "dblclick",
        "mousedown",
        "mouseup",
        "mouseover",
        "mouseout",
        "mousemove",
        "contextmenu",
      ];

      events.forEach(function (event) {
        L.DomEvent.on(layer._text, event, layer.fire, layer);
      });
    }
  },

  _updateTextPath: function (layer) {
    const id = "path-" + L.Util.stamp(layer),
      path = layer._path,
      textPath = layer._textPath;

    if (!path.getAttribute("id")) {
      path.setAttribute("id", id);
      textPath.setAttributeNS(
        "http://www.w3.org/1999/xlink",
        "xlink:href",
        "#" + id,
      );
    }
  },

  _removeTextPath: function (layer) {
    if (layer.options.interactive) {
      const events = [
        "click",
        "dblclick",
        "mousedown",
        "mouseup",
        "mouseover",
        "mouseout",
        "mousemove",
        "contextmenu",
      ];
      events.forEach(function (event) {
        L.DomEvent.off(layer._text, event, layer.fire, layer);
      });
    }

    L.DomUtil.remove(layer._text);
    layer._textPath = null;
    layer._text = null;
    layer.removeInteractiveTarget(layer._text);
  },

  _updateTextStyle: function (layer) {
    const text = layer._text,
      textPath = layer._textPath,
      options = layer.options;

    if (!text || !textPath) {
      return;
    }

    if (options.textStyle) {
      for (const k in options.textStyle) {
        text.setAttribute(k, options.textStyle[k]);
      }
    }

    if (options.outlineStroke && options.outlineStroke != "none") {
      const [strokeWidth, strokeColor] = options.outlineStroke.split(" ", 2);
      text.setAttribute("stroke", strokeColor);
      text.setAttribute("stroke-width", strokeWidth);
      text.setAttribute("letter-spacing", strokeWidth);
    }

    text.setAttribute("dy", options.textDy || "0.33em");
    textPath.setAttribute("method", options.textMethod || "stretch");
    textPath.setAttribute("spacing", options.textSpacing || "auto");
    textPath.setAttribute("startOffset", options.textStartOffset || "50%");
    textPath.setAttribute("text-anchor", options.textAnchor || "middle");
  },
});

L.svg.textPath = function (options) {
  return new L.SVG.TextPath(options);
};

L.Map.include({
  _createRenderer: function (options) {
    // @namespace Map; @option preferCanvas: Boolean = false
    // Whether `Path`s should be rendered on a `Canvas` renderer.
    // By default, all `Path`s are rendered in a `SVG` renderer.
    return (
      (this.options.preferCanvas && L.canvas(options)) ||
      L.svg.textPath(options)
    );
  },
});

L.Path.include({
  getText: function () {
    return this.options.text;
  },

  setText: function (text) {
    this.options.text = text;
    return this.redraw();
  },
});
