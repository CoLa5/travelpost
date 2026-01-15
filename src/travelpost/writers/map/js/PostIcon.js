if (typeof L.Travel === "undefined") {
  L.Travel = {};
}

L.Travel.PostIcon = L.Icon.extend({
  options: {
    imgUrl: null,
    iconShape: "circle", // "rounded-square", "square"
    iconSize: 32,
    emptySize: 16,

    backgroundColor: "#3388ff",
    borderColor: "white",
    borderWidth: 2,
    borderStyle: "solid",
    className: "",
  },

  createIcon: function (oldIcon) {
    const div =
      oldIcon && oldIcon.tagName === "DIV"
        ? oldIcon
        : document.createElement("div");

    div.innerHTML = "";

    this._setIconStyles(div);

    return div;
  },

  createShadow: function () {
    return null;
  },

  _setIconStyles: function (iconDiv) {
    const options = this.options,
      s = options.imgUrl ? options.iconSize : options.emptySize,
      size = L.point(s, s),
      anchor = L.point(s / 2, s / 2 - 1);

    iconDiv.className = "leaflet-marker-icon post-icon";
    if (options.iconShape) {
      iconDiv.className += " " + options.iconShape;
    }
    if (options.className) {
      iconDiv.className += " " + options.className;
    }
    if (options.imgUrl) {
      iconDiv.style.backgroundImage = `url('${options.imgUrl}')`;
    } else {
      iconDiv.style.backgroundColor = options.backgroundColor;
    }
    if (options.borderColor && options.borderWidth) {
      iconDiv.style.borderColor = options.borderColor;
      iconDiv.style.borderStyle = options.borderStyle;
      iconDiv.style.borderWidth = options.borderWidth + "px";
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

L.Travel.postIcon = function (options) {
  return new L.Travel.PostIcon(options);
};
