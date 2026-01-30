"""Title - Publisher Logo."""

from travelpost.writers.pdf.flowables.condor_eye import CondorEye
from travelpost.writers.pdf.libs.reportlab.platypus import ParagraphStyle
from travelpost.writers.pdf.styles import get_style


def initials(author: str) -> str:
    return "".join(a[0].upper() for a in author.split(" "))


class PublisherLogo(CondorEye):
    """Publisher Logo."""

    STYLE: ParagraphStyle = get_style("publisher_logo")

    def __init__(self, author: str) -> None:
        """Initializes the publisher logo.

        Args:
            author: The author name whose initials to use in the logo.
        """
        super().__init__(initials(author))
