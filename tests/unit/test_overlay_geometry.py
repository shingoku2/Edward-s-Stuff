"""
Unit tests for OverlayWindow geometry save/restore.

Tests that the overlay window properly saves its position, size,
and minimized state through the debounced timer mechanism.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


@pytest.mark.unit
class TestOverlayWindowGeometry:
    """Test OverlayWindow geometry saving via move/resize events."""

    def test_overlay_window_has_required_geometry_methods(self):
        """Test that OverlayWindow has the required geometry-related methods."""
        from src.gui import OverlayWindow

        # Verify the required methods exist
        assert hasattr(OverlayWindow, 'moveEvent')
        assert hasattr(OverlayWindow, 'resizeEvent')
        assert hasattr(OverlayWindow, '_save_geometry')

        # Verify they are callable
        assert callable(getattr(OverlayWindow, 'moveEvent'))
        assert callable(getattr(OverlayWindow, 'resizeEvent'))
        assert callable(getattr(OverlayWindow, '_save_geometry'))

    def test_move_event_triggers_save_timer(self):
        """Test that moveEvent starts the debounced save timer."""
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.OmnixDesignSystem') as mock_ds:

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            mock_ds_instance = MagicMock()
            mock_ds_instance.get_overlay_stylesheet.return_value = ""
            mock_ds.return_value = mock_ds_instance

            from src.gui import OverlayWindow

            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8
            mock_config.save = Mock()

            overlay = OverlayWindow(None, mock_config, mock_ds_instance)

            # Get the moveEvent method
            move_event_method = overlay.moveEvent

            # Create a mock event
            mock_event = MagicMock()

            # Call moveEvent
            move_event_method(mock_event)

            # Verify timer was started with 400ms delay
            mock_timer.start.assert_called_once_with(400)

    def test_resize_event_triggers_save_timer(self):
        """Test that resizeEvent starts the debounced save timer."""
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.OmnixDesignSystem') as mock_ds:

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            mock_ds_instance = MagicMock()
            mock_ds_instance.get_overlay_stylesheet.return_value = ""
            mock_ds.return_value = mock_ds_instance

            from src.gui import OverlayWindow

            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8
            mock_config.save = Mock()

            overlay = OverlayWindow(None, mock_config, mock_ds_instance)

            # Get the resizeEvent method
            resize_event_method = overlay.resizeEvent

            # Create a mock event
            mock_event = MagicMock()

            # Call resizeEvent
            resize_event_method(mock_event)

            # Verify timer was started with 400ms delay
            mock_timer.start.assert_called_once_with(400)

    def test_save_geometry_updates_config_and_saves(self):
        """Test that _save_geometry updates config with current position/size."""
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.OmnixDesignSystem') as mock_ds:

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            mock_ds_instance = MagicMock()
            mock_ds_instance.get_overlay_stylesheet.return_value = ""
            mock_ds.return_value = mock_ds_instance

            from src.gui import OverlayWindow

            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8
            mock_config.save = Mock()

            overlay = OverlayWindow(None, mock_config, mock_ds_instance)

            # Mock the overlay's current geometry
            overlay.move = Mock()
            overlay.x = Mock(return_value=200)
            overlay.y = Mock(return_value=300)
            overlay.width = Mock(return_value=500)
            overlay.height = Mock(return_value=400)

            # Call _save_geometry
            overlay._save_geometry()

            # Verify config was updated
            assert mock_config.overlay_x == 200
            assert mock_config.overlay_y == 300
            assert mock_config.overlay_width == 500
            assert mock_config.overlay_height == 400

            # Verify save was called
            mock_config.save.assert_called_once()

    def test_minimize_state_is_tracked(self):
        """Test that minimized state is properly tracked."""
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.OmnixDesignSystem') as mock_ds:

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            mock_ds_instance = MagicMock()
            mock_ds_instance.get_overlay_stylesheet.return_value = ""
            mock_ds.return_value = mock_ds_instance

            from src.gui import OverlayWindow

            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = True  # Start minimized
            mock_config.overlay_opacity = 0.8
            mock_config.save = Mock()

            overlay = OverlayWindow(None, mock_config, mock_ds_instance)

            # Verify minimized state is tracked
            assert overlay._minimized is True


@pytest.mark.unit
class TestOverlayWindowDragging:
    """Test OverlayWindow drag-to-move functionality."""

    def test_mouse_press_sets_drag_position(self):
        """Test that left mouse press sets up drag position."""
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.OmnixDesignSystem') as mock_ds:

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            mock_ds_instance = MagicMock()
            mock_ds_instance.get_overlay_stylesheet.return_value = ""
            mock_ds.return_value = mock_ds_instance

            from src.gui import OverlayWindow
            from PyQt6.QtCore import Qt

            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8
            mock_config.save = Mock()

            overlay = OverlayWindow(None, mock_config, mock_ds_instance)

            # Create mock mouse event
            mock_event = MagicMock()
            mock_event.button.return_value = Qt.MouseButton.LeftButton
            mock_event.globalPosition.return_value.toPoint.return_value = (150, 200)
            overlay.frameGeometry = MagicMock()
            overlay.frameGeometry.return_value.topLeft.return_value = (100, 100)

            # Call mousePressEvent
            overlay.mousePressEvent(mock_event)

            # Verify _drag_pos was set
            assert overlay._drag_pos is not None

    def test_mouse_move_drags_window(self):
        """Test that mouse move with drag position moves the window."""
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.OmnixDesignSystem') as mock_ds:

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            mock_ds_instance = MagicMock()
            mock_ds_instance.get_overlay_stylesheet.return_value = ""
            mock_ds.return_value = mock_ds_instance

            from src.gui import OverlayWindow
            from PyQt6.QtCore import Qt

            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8
            mock_config.save = Mock()

            overlay = OverlayWindow(None, mock_config, mock_ds_instance)

            # Set up drag position
            overlay._drag_pos = (50, 60)

            # Create mock mouse event
            mock_event = MagicMock()
            mock_event.buttons.return_value = Qt.MouseButton.LeftButton
            mock_event.globalPosition.return_value.toPoint.return_value = (200, 250)
            overlay.move = MagicMock()

            # Call mouseMoveEvent
            overlay.mouseMoveEvent(mock_event)

            # Verify move was called
            overlay.move.assert_called_once()

    def test_mouse_release_clears_drag_position(self):
        """Test that mouse release clears drag position."""
        with patch('src.gui.QTimer') as mock_timer_class, \
             patch('src.gui.OmnixDesignSystem') as mock_ds:

            mock_timer = MagicMock()
            mock_timer_class.return_value = mock_timer

            mock_ds_instance = MagicMock()
            mock_ds_instance.get_overlay_stylesheet.return_value = ""
            mock_ds.return_value = mock_ds_instance

            from src.gui import OverlayWindow

            mock_config = Mock()
            mock_config.overlay_x = 100
            mock_config.overlay_y = 100
            mock_config.overlay_width = 420
            mock_config.overlay_height = 360
            mock_config.overlay_minimized = False
            mock_config.overlay_opacity = 0.8
            mock_config.save = Mock()

            overlay = OverlayWindow(None, mock_config, mock_ds_instance)

            # Set up drag position
            overlay._drag_pos = (50, 60)

            # Create mock mouse event
            mock_event = MagicMock()

            # Call mouseReleaseEvent
            overlay.mouseReleaseEvent(mock_event)

            # Verify _drag_pos was cleared
            assert overlay._drag_pos is None