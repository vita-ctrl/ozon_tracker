from abc import ABC, abstractmethod

from ..models import ProductDataDict
from ..widget_states import WidgetStates


class WidgetExtractor(ABC):
    @abstractmethod
    def extract(self, states: WidgetStates) -> ProductDataDict:
        """Returns a partially filled product data dictionary."""
