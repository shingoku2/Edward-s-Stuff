"""
HexStatusWidget Widget
"""
import math
from typing import Optional

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QLabel, QWidget


class HexStatusWidget(QWidget):
    """Custom-drawn hexagon container for game status display."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMinimumSize(240, 240)
        self.setObjectName("HexWidget")
        self.icon_label = QLabel("◎", self)
        self.icon_label.setObjectName("HexIcon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_label = QLabel("CSGO", self)
        self.game_label.setObjectName("HexGameLabel")
        self.game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label = QLabel("ONLINE", self)
        self.status_label.setObjectName("HexStatusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._position_labels()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_labels()

    def _position_labels(self):
        center = self.rect().center()
        self.icon_label.resize(int(self.width() * 0.35), int(self.height() * 0.35))
        self.icon_label.move(
            center.x() - self.icon_label.width() // 2, center.y() - self.icon_label.height()
        )
        self.game_label.resize(int(self.width() * 0.5), int(self.height() * 0.2))
        self.game_label.move(
            center.x() - self.game_label.width() // 2, center.y() - self.game_label.height() // 4
        )
        self.status_label.resize(int(self.width() * 0.45), 26)
        self.status_label.move(
            center.x() - self.status_label.width() // 2, center.y() + self.game_label.height() // 2
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = rect.center().x() + rect.width() / 2 * 0.86 * math.cos(angle_rad)
            y = rect.center().y() + rect.height() / 2 * 0.86 * math.sin(angle_rad)
            points.append(QPointF(x, y))

        gradient = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomRight()))
        gradient.setColorAt(0, QColor(5, 189, 255, 60))
        gradient.setColorAt(1, QColor(75, 88, 210, 90))
        painter.setBrush(gradient)
        painter.setPen(QColor(12, 209, 255, 210))
        painter.drawPolygon(points)

        inner_rect = rect.adjusted(12, 12, -12, -12)
        inner_points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = inner_rect.center().x() + inner_rect.width() / 2 * 0.86 * math.cos(angle_rad)
            y = inner_rect.center().y() + inner_rect.height() / 2 * 0.86 * math.sin(angle_rad)
            inner_points.append(QPointF(x, y))

        painter.setBrush(QColor(7, 18, 45, 180))
        painter.setPen(QColor(255, 66, 66, 180))
        painter.drawPolygon(inner_points)
