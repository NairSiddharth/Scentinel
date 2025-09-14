#!/usr/bin/env python3
"""
Base tab class for Scentinel application tabs.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from ..database import Database


class BaseTab(ABC):
    """Abstract base class for all application tabs"""

    def __init__(self, database: Database):
        self.db = database
        self.container: Optional[Any] = None

    @abstractmethod
    def setup_tab_content(self, container: Any) -> None:
        """Setup the tab content UI within the provided container"""
        pass

    def refresh_data(self) -> None:
        """Refresh tab data - override if needed"""
        pass

    def cleanup(self) -> None:
        """Cleanup resources - override if needed"""
        pass