if (typeof L.Travel === "undefined") {
  L.Travel = {};
}

L.Travel.PostIcon = L.Icon.extend({
  options: {
    imgUrl: null,
    iconShape: "circle", // "rounded-square", "square"
    emptySize: 16,
    imgSize: 32,

    backgroundColor: "#3388ff",
    borderColor: "white",
    borderWidth: 2,
    borderStyle: "solid",
    className: "",
  },

  initialize: function (options) {
    L.Util.setOptions(this, options);
    const size = this.options.imgUrl
      ? this.options.imgSize
      : this.options.emptySize;

    this.options.iconSize = [size, size];
    this.options.iconAnchor = [
      this.options.iconSize[0] / 2,
      this.options.iconSize[1] / 2 - 1,
    ];
    this.options.popupAnchor = [0, this.options.iconSize[1] / 2];
    this.options.tooltipAnchor = [0, -this.options.iconSize[1] / 2];
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
      size = L.point(options.iconSize),
      anchor = L.point(options.iconAnchor);

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
