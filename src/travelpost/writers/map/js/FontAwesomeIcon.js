if (typeof L.Travel === "undefined") {
  L.Travel = {};
}

L.Travel.FAIcon = L.Icon.extend({
  options: {
    icon: "leaf",
    iconClassName: "",
    iconPadding: 8,
    iconShape: "square", // "circle", "rounded-square", "square"
    iconSize: [32, 32],
    iconStyle: "solid",

    backgroundColor: "unset",
    borderColor: "unset",
    borderWidth: 0,
    borderStyle: "solid",
    className: "",
    color: "black",

    outlineStroke: "none",
  },

  initialize: function (options) {
    if (typeof options.iconSize === "number") {
      options.iconSize = [options.iconSize, options.iconSize];
    }
    L.Util.setOptions(this, options);

    this.options.iconAnchor = [
      Math.floor(this.options.iconSize[0] / 2),
      Math.floor(this.options.iconSize[1] / 2),
    ];
    this.options.popupAnchor = [0, Math.floor(this.options.iconSize[1] / 2)];
    this.options.tooltipAnchor = [0, -Math.floor(this.options.iconSize[1] / 2)];
  },

  createIcon: function (oldIcon) {
    const div =
      oldIcon && oldIcon.tagName === "DIV"
        ? oldIcon
        : document.createElement("div");
    div.className = "leaflet-marker-icon";

    this.createIElement(div);
    this._setIconStyles(div);

    return div;
  },


  createIElement: function (div, outlineStroke = false) {
    let i = div.querySelector(":scope > i");
    if (i === null) {
      i = document.createElement("i");
      div.appendChild(i);
    }

    const options = this.options,
      iconStyle = options.iconStyle.startsWith("fa-")
        ? options.iconStyle
        : "fa-" + options.iconStyle,
      iconLabel = options.icon.startsWith("fa-")
        ? options.icon
        : "fa-" + options.icon;

    i.className = iconStyle + " " + iconLabel;
    if (options.iconClassName) {
      i.className += " " + options.iconClassName;
    }
    if (
      outlineStroke &&
      options.outlineStroke &&
      options.outlineStroke != "none"
    ) {
      i.className += " " + "outline";
      i.style.setProperty("--text-stroke", options.outlineStroke);
    }
  },

  _setIconStyles: function (iconDiv) {
    const options = this.options,
      fontSize = options.iconSize[1] - 2 * options.iconPadding,
      size = L.point(options.iconSize),
      anchor = L.point(options.iconAnchor);

    if (iconDiv.className) iconDiv.className += " ";
    iconDiv.className += "fa-marker-icon";

    if (options.iconShape) {
      iconDiv.className += " " + options.iconShape;
    }
    if (options.className) {
      iconDiv.className += " " + options.className;
    }

    if (options.backgroundColor) {
      iconDiv.style.backgroundColor = options.backgroundColor;
    }
    if (options.borderColor && options.borderStyle && options.borderWidth) {
      iconDiv.style.borderColor = options.borderColor;
      iconDiv.style.borderStyle = options.borderStyle;
      iconDiv.style.borderWidth = options.borderWidth + "px";
    }
    if (options.color) {
      iconDiv.style.color = options.color;
    }

    if (fontSize) {
      iconDiv.style.fontSize = fontSize + "px";
    }

    if (anchor) {
      iconDiv.style.marginLeft = -anchor.x + "px";
      iconDiv.style.marginTop = -anchor.y + "px";
    }

    if (size) {
      iconDiv.style.width = size.x + "px";
      iconDiv.style.height = size.y + "px";
    }
  },
});

L.Travel.faIcon = function (options) {
  return new L.Travel.FAIcon(options);
};
