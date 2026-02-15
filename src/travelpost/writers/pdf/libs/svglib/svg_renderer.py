"""Svg Renderer Patch (original: :py:cls:`svglib.svglib.SvgRenderer`)."""

from collections import defaultdict
from collections.abc import Callable
import logging
import os
from typing import Any

from reportlab.graphics.shapes import Group
from reportlab.lib.colors import Color
from svglib import svglib
from svglib.fonts import FontMap

from travelpost.writers.pdf.libs.svglib.converter import (
    Svg2RlgAttributeConverter,
)
from travelpost.writers.pdf.libs.svglib.converter import Svg2RlgShapeConverter

logger = logging.getLogger(f"{svglib.logger.name:s}.patch")


class SvgRenderer(svglib.SvgRenderer):
    def __init__(
        self,
        path: str | os.PathLike[str],
        color_converter: Callable[[Color], Color] | None = None,
        parent_svgs: list[str] | None = None,
        font_map: FontMap | None = None,
    ) -> None:
        self.source_path = path
        self._parent_chain = parent_svgs or []  # To detect circular refs.
        self.attrConverter = Svg2RlgAttributeConverter(
            color_converter=color_converter,
            font_map=font_map,
        )
        self.shape_converter = Svg2RlgShapeConverter(
            path,
            self.attrConverter,
        )
        self.handled_shapes = self.shape_converter.get_handled_shapes()
        self.definitions: dict[str, Any] = {}
        self.waiting_use_nodes: dict[
            str, list[tuple[svglib.NodeTracker, Any | None]]
        ] = defaultdict(list)
        self._external_svgs: dict[str, svglib.ExternalSVG] = {}
        self.attrConverter.css_rules = svglib.CSSMatcher()

    def renderNode(
        self,
        node: svglib.NodeTracker,
        parent: Any | None = None,
    ) -> None:
        """Render a single SVG node and add it to a parent group.

        Args:
            node: The NodeTracker object for the SVG node.
            parent: The parent ReportLab Group to add the rendered object to.
        """
        if parent is None:
            return
        nid = node.getAttribute("id")
        ignored = False
        item = None
        name = svglib.node_name(node)

        clipping = self.get_clippath(node)
        if name == "svg":
            item = self.renderSvg(node)
            parent.add(item)
        elif name == "defs":
            ignored = True  # defs are handled in the initial rendering phase.
        elif name == "a":
            item = self.renderA(node)
            parent.add(item)
        elif name == "g":
            display = node.getAttribute("display")
            item = self.renderG(node, clipping=clipping)
            if display != "none":
                parent.add(item)
        elif name == "style":
            self.renderStyle(node)
        elif name == "symbol":
            item = self.renderSymbol(node)
            # First time the symbol node is rendered, it should not be part of a
            # group. It is only rendered to be part of definitions.
            if node.attrib.get("_rendered"):
                parent.add(item)
            else:
                node.set("_rendered", "1")
        elif name == "use":
            item = self.renderUse(node, clipping=clipping)
            parent.add(item)
        # TODO: pattern & mask
        elif name in {"clipPath", "linearGradient", "radialGradient"}:
            item = self.renderG(node)
        elif name in self.handled_shapes:
            if name == "image":
                # We resolve the image target at renderer level because it can
                # point to another SVG file or node which has to be rendered
                # stoo.
                target = self.xlink_href_target(node)
                if target is None:
                    return
                elif isinstance(target, tuple):
                    # This is SVG content needed to be rendered
                    gr = Group()
                    renderer, img_node = target
                    renderer.renderNode(img_node, parent=gr)
                    self.apply_node_attr_to_group(node, gr)
                    parent.add(gr)
                    return
                else:
                    # Attaching target to node, so we can get it back in
                    # convertImage
                    node._resolved_target = target

            item = self.shape_converter.convertShape(
                name,
                node,
                definitions=self.definitions,
            )
            display = node.getAttribute("display")
            if item and display != "none":
                parent.add(item)
        else:
            ignored = True
            logger.debug("Ignoring node: %s", name)

        if not ignored:
            if nid and item:
                self.definitions[nid] = node
                # preserve id to keep track of svg objects
                # and simplify further analyses of generated document
                item.setProperties({"svgid": nid})
                # labels are used in inkscape to name specific groups as layers
                # preserving them simplify extraction of feature from the
                # generated document
                label_attrs = [
                    v for k, v in node.attrib.items() if "label" in k
                ]
                if len(label_attrs) == 1:
                    (label,) = label_attrs
                    item.setProperties({"label": label})
            if nid in self.waiting_use_nodes:
                to_render = self.waiting_use_nodes.pop(nid)
                for use_node, group in to_render:
                    self.renderUse(use_node, group=group)
            self.print_unused_attributes(node)
