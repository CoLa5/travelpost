if (typeof L.Travel === "undefined") {
  L.Travel = {};
}

L.Travel.FAIcon = L.Icon.extend({
  options: {
    icon: "leaf",
    iconClassName: "",
    iconShape: "circle", // "rounded-square", "square"
    iconSize: 32,
    iconStyle: "solid",

    backgroundColor: "#3388ff",
    borderColor: "white",
    borderWidth: 2,
    borderStyle: "solid",
    className: "",
    color: "white",
    fontSize: 18,
  },

  createIcon: function (oldIcon) {
    const div =
      oldIcon && oldIcon.tagName === "DIV"
        ? oldIcon
        : document.createElement("div");

    div.innerHTML = this.createIconInnerHtml();

    this._setIconStyles(div);

    return div;
  },

  createIconInnerHtml: function () {
    const options = this.options,
      iconStyle = options.iconStyle.startsWith("fa-")
        ? options.iconStyle
        : "fa-" + options.iconStyle,
      icon = options.icon.startsWith("fa-")
        ? options.icon
        : "fa-" + options.icon;
    return (
      '<i class="' +
      iconStyle +
      " " +
      icon +
      " " +
      (options.iconClassName || "") +
      '"></i>'
    );
  },

  createShadow: function () {
    return null;
  },

  _setIconStyles: function (iconDiv) {
    const options = this.options,
      size = L.point(options.iconSize, options.iconSize),
      anchor = L.point(options.iconSize / 2, options.iconSize / 2 - 1);

    iconDiv.className = "leaflet-marker-icon fa-marker-icon";
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
    if (options.fontSize) {
      iconDiv.style.fontSize = options.fontSize + "px";
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
