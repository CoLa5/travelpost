"""Monkey Patch."""

from typing import Any


def monkey_patch_reportlab_renderPath() -> None:
    """Apply a patch to ReportLab to handle path fill rules correctly.

    This patch addresses an issue where ReportLab does not honor the
    'fill-rule' attribute of SVG paths, defaulting to 'even-odd'.
    """
    from reportlab.graphics import shapes

    original_renderPath = shapes._renderPath

    def patchedRenderPath(
        path: shapes.Path,
        drawFuncs: Any,
        **kwargs: Any,
    ) -> Any:
        # Patched method to transfer fillRule from Path to PDFPathObject
        # Get back from bound method to instance
        if len(drawFuncs) == 4:
            drawFuncs = (
                *drawFuncs,
                drawFuncs[0].__self__.ellipse,
                drawFuncs[0].__self__.rect,
            )
        return original_renderPath(path, drawFuncs, **kwargs)

    shapes._renderPath = patchedRenderPath
