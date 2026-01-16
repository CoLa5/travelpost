"""To PNG."""

from collections.abc import Sequence
import logging
import time
import timeit
from typing import Any

import folium
from folium.utilities import temp_html_filepath
from selenium.webdriver.support.ui import WebDriverWait

POLL_FREQUENCY: float = 0.1
logger = logging.getLogger(__name__)


def to_png(
    map: folium.Map,
    poll_frequency: float = 0.5,
    max_delay: float = 3.0,
    driver: Any = None,
    size: Sequence[int] | None = None,
) -> bytes:
    """Export the HTML to byte representation of a PNG image.

    Uses selenium to render the HTML and record a PNG. You may need to adjust
    the `poll_frequency` and `max_delay` keyword argument if maps render without
    data or tiles.

    Uses a headless Firefox webdriver by default, though you can provide your
    own.

    Examples
    --------
    >>> m._to_png()
    >>> m._to_png(time=10)  # Wait 10 seconds between render and snapshot.

    """
    logger.info("Printing map ...")
    start = timeit.default_timer()

    if driver is None:
        from selenium import webdriver

        options = webdriver.firefox.options.Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)

    if size is None:
        driver.fullscreen_window()
    else:
        window_size = driver.execute_script(
            """
            return [window.outerWidth - window.innerWidth + arguments[0],
                window.outerHeight - window.innerHeight + arguments[1]];
            """,
            *size,
        )
        driver.set_window_size(*window_size)

    html = map.get_root().render()
    with temp_html_filepath(html) as fname:
        # We need the tempfile to avoid JS security issues.
        driver.get(f"file:///{fname:s}")
        WebDriverWait(driver, max_delay, poll_frequency=poll_frequency).until(
            lambda d: d.find_element(
                "class name", "tile-loading-control"
            ).get_attribute("data-ready")
            == "true"
        )
        # NOTE: See source code of Leaflet GridLayer at:
        #       https://github.com/Leaflet/Leaflet/blob/d15112c9e8ac339f0f74f563959d0423d291308d/src/layer/tile/GridLayer.js#L885C1-L886C29
        if map.options.get("fade_animation", True):
            time.sleep(0.25)
        div = driver.find_element("class name", "folium-map")
        png = div.screenshot_as_png
        driver.quit()

    end = timeit.default_timer()
    logger.info("Printed map in %.2f s", end - start)
    return png
