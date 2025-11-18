"""Document AI API module."""
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from money_api.client import MoneyAPI


class DocumentAPI:
    """Document AI operations."""

    def __init__(self, client: "MoneyAPI"):
        self.client = client
