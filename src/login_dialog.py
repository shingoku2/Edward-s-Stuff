"""Login dialog using QWebEngineView for provider authentication."""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """Generic web-based login dialog for AI providers."""

    session_acquired = pyqtSignal(dict)

    def __init__(
        self,
        parent=None,
        *,
        provider: str,
        login_url: str,
        success_url_prefixes: Optional[List[str]] = None,
        required_cookies: Optional[List[str]] = None,
    ) -> None:
        super().__init__(parent)
        self.provider = provider
        self.login_url = login_url
        self.success_url_prefixes = success_url_prefixes or []
        self.required_cookies = set(required_cookies or [])
        self._cookies: Dict[str, Dict[str, str]] = {}

        self.setWindowTitle(f"Sign in to {self.provider.title()}")
        self.resize(900, 700)
        self._init_ui()
        self._load_login_page()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        instruction = QLabel(
            "Sign in using the embedded browser. When authentication completes, "
            "click \"Use Session\" to capture cookies for this provider."
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        self.web_view = QWebEngineView(self)
        self.profile = QWebEngineProfile(self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.page = QWebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.page)
        self.web_view.urlChanged.connect(self._on_url_changed)
        self.profile.cookieStore().cookieAdded.connect(self._on_cookie_added)
        self.cookie_store = self.profile.cookieStore()
        layout.addWidget(self.web_view, stretch=1)

        button_row = QHBoxLayout()

        self.use_session_button = QPushButton("Use Session")
        self.use_session_button.clicked.connect(self._emit_session)
        button_row.addWidget(self.use_session_button)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self._load_login_page)
        button_row.addWidget(self.reload_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_button)

        layout.addLayout(button_row)

    def _load_login_page(self) -> None:
        logger.info("Launching login page for %s", self.provider)
        self.web_view.setUrl(QUrl(self.login_url))

    def _on_cookie_added(self, cookie) -> None:  # pragma: no cover - Qt signal
        try:
            domain = cookie.domain()
            name = cookie.name().data().decode()
            value = cookie.value().data().decode()
            logger.debug("Cookie added for %s: %s=%s", domain, name, value[:4] + "...")
            self._cookies[name] = {
                "name": name,
                "value": value,
                "domain": domain,
                "path": cookie.path(),
                "isSecure": cookie.isSecure(),
                "isHttpOnly": cookie.isHttpOnly(),
            }
            if self.required_cookies and self.required_cookies.issubset(self._cookies.keys()):
                logger.info("Required cookies captured for %s", self.provider)
                self._emit_session()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to process cookie for %s: %s", self.provider, exc)

    def _on_url_changed(self, url: QUrl) -> None:  # pragma: no cover - Qt signal
        url_str = url.toString()
        logger.debug("%s URL changed: %s", self.provider, url_str)
        if any(url_str.startswith(prefix) for prefix in self.success_url_prefixes):
            logger.info("Detected successful redirect for %s", self.provider)
            self._emit_session(url_str)

    def _emit_session(self, final_url: Optional[str] = None) -> None:
        if final_url is None:
            final_url = self.web_view.url().toString()

        if not self._cookies:
            logger.warning("No cookies captured yet for %s", self.provider)

        session_payload = {
            "provider": self.provider,
            "final_url": final_url,
            "cookies": list(self._cookies.values()),
        }
        logger.info(
            "Emitting session data for %s with %d cookies", self.provider, len(self._cookies)
        )
        try:
            self.session_acquired.emit(session_payload)
        finally:
            self.accept()

    def get_serialized_session(self) -> str:
        """Return the current session payload as JSON."""
        return json.dumps(
            {
                "provider": self.provider,
                "cookies": list(self._cookies.values()),
            }
        )
