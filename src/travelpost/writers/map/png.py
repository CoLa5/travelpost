"""To PNG."""

from collections.abc import Sequence
import time
from typing import Any

import folium
from folium.utilities import temp_html_filepath
from selenium.webdriver.support.ui import WebDriverWait

POLL_FREQUENCY: float = 0.25


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
        time.sleep(poll_frequency)
        div = driver.find_element("class name", "folium-map")
        png = div.screenshot_as_png
        driver.quit()
    return png
