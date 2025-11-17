"""
Omnix Theme Manager (New Implementation)
=========================================

Modern theme manager that works directly with the Omnix design system.
Replaces the legacy src/theme_manager.py with a token-based approach.

This implementation:
- Works directly with OmnixDesignTokens
- Supports dynamic theme updates
- Persists user customizations
- Migrates legacy theme configurations
- Provides real-time UI updates
"""

import os
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import asdict

from .tokens import OmnixDesignTokens, COLORS, TYPOGRAPHY, SPACING, RADIUS
from .design_system import OmnixDesignSystem

logger = logging.getLogger(__name__)


class OmnixThemeManager:
    """
    Modern theme manager for Omnix UI using the design token system.

    Features:
    - Direct token manipulation
    - Real-time UI updates via callbacks
    - Theme persistence
    - Legacy theme migration
    - Extensible customization
    """

    def __init__(self, config_dir: str = None):
        """
        Initialize theme manager.

        Args:
            config_dir: Configuration directory path (defaults to ~/.gaming_ai_assistant)
        """
        self.config_dir = config_dir or os.path.expanduser("~/.gaming_ai_assistant")
        self.config_file = os.path.join(self.config_dir, "theme.json")
        self.backup_file = os.path.join(self.config_dir, "theme.json.backup")

        # Initialize design system
        self.tokens = OmnixDesignTokens()
        self.design_system = OmnixDesignSystem()

        # Callbacks for UI updates
        self._update_callbacks: List[Callable] = []

        # User customizations tracking
        self._customized_tokens = set()

        # Load saved theme if exists
        self._load_theme()

    # ==================== Theme Loading & Saving ====================

    def _load_theme(self):
        """Load theme from configuration file."""
        try:
            if not os.path.exists(self.config_file):
                logger.info("No theme configuration found, using defaults")
                return

            with open(self.config_file, 'r') as f:
                data = json.load(f)

            # Check version and migrate if needed
            version = data.get('version', 1)

            if version == 1:
                logger.info("Migrating legacy theme configuration to v2")
                self._migrate_legacy_theme(data)
            elif version == 2:
                self._load_v2_theme(data)
            else:
                logger.warning(f"Unknown theme version {version}, using defaults")

            logger.info("Theme configuration loaded successfully")

        except Exception as e:
            logger.error(f"Error loading theme configuration: {e}")
            logger.info("Using default theme")

    def _load_v2_theme(self, data: Dict[str, Any]):
        """
        Load version 2 theme format.

        Args:
            data: Theme configuration dictionary
        """
        tokens_data = data.get('tokens', {})

        # Load color customizations
        if 'colors' in tokens_data:
            for key, value in tokens_data['colors'].items():
                if hasattr(self.tokens.colors, key):
                    setattr(self.tokens.colors, key, value)
                    self._customized_tokens.add(f"colors.{key}")

        # Load typography customizations
        if 'typography' in tokens_data:
            for key, value in tokens_data['typography'].items():
                if hasattr(self.tokens.typography, key):
                    setattr(self.tokens.typography, key, value)
                    self._customized_tokens.add(f"typography.{key}")

        # Load spacing customizations
        if 'spacing' in tokens_data:
            for key, value in tokens_data['spacing'].items():
                if hasattr(self.tokens.spacing, key):
                    setattr(self.tokens.spacing, key, value)
                    self._customized_tokens.add(f"spacing.{key}")

        # Load radius customizations
        if 'radius' in tokens_data:
            for key, value in tokens_data['radius'].items():
                if hasattr(self.tokens.radius, key):
                    setattr(self.tokens.radius, key, value)
                    self._customized_tokens.add(f"radius.{key}")

        logger.info(f"Loaded {len(self._customized_tokens)} customized tokens")

    def save_theme(self):
        """Save current theme configuration to file."""
        try:
            # Ensure config directory exists
            os.makedirs(self.config_dir, exist_ok=True)

            # Create backup if file exists
            if os.path.exists(self.config_file):
                shutil.copy(self.config_file, self.backup_file)

            # Prepare theme data
            theme_data = {
                'version': 2,
                'timestamp': datetime.now().isoformat(),
                'tokens': {
                    'colors': asdict(self.tokens.colors),
                    'typography': asdict(self.tokens.typography),
                    'spacing': asdict(self.tokens.spacing),
                    'radius': asdict(self.tokens.radius),
                },
                'customizations': {
                    'modified_tokens': list(self._customized_tokens),
                    'count': len(self._customized_tokens)
                }
            }

            # Write to file
            with open(self.config_file, 'w') as f:
                json.dump(theme_data, f, indent=2)

            logger.info(f"Theme saved successfully ({len(self._customized_tokens)} customizations)")

        except Exception as e:
            logger.error(f"Error saving theme: {e}")

    def _migrate_legacy_theme(self, legacy_data: Dict[str, Any]):
        """
        Migrate legacy theme.json (v1) to new format (v2).

        Args:
            legacy_data: Old theme configuration
        """
        logger.info("Migrating legacy theme configuration")

        legacy_theme = legacy_data.get('theme', {})

        # Map legacy colors to new tokens
        color_mapping = {
            'primary_color': 'accent_primary',
            'secondary_color': 'accent_secondary',
            'background_color': 'bg_primary',
            'surface_color': 'bg_secondary',
            'text_color': 'text_primary',
            'text_secondary_color': 'text_secondary',
            'error_color': 'error',
            'success_color': 'success',
            'warning_color': 'warning',
        }

        for legacy_key, new_key in color_mapping.items():
            if legacy_key in legacy_theme:
                value = legacy_theme[legacy_key]
                setattr(self.tokens.colors, new_key, value)
                self._customized_tokens.add(f"colors.{new_key}")
                logger.debug(f"Migrated {legacy_key} -> {new_key}: {value}")

        # Map legacy typography
        if 'font_family' in legacy_theme:
            self.tokens.typography.font_primary = legacy_theme['font_family']
            self._customized_tokens.add('typography.font_primary')

        if 'font_size' in legacy_theme:
            self.tokens.typography.size_base = legacy_theme['font_size']
            self._customized_tokens.add('typography.size_base')

        # Map legacy spacing
        if 'spacing' in legacy_theme:
            self.tokens.spacing.base = legacy_theme['spacing']
            self._customized_tokens.add('spacing.base')

        if 'border_radius' in legacy_theme:
            self.tokens.radius.base = legacy_theme['border_radius']
            self._customized_tokens.add('radius.base')

        # Save migrated theme
        self.save_theme()
        logger.info(f"Legacy theme migrated successfully ({len(self._customized_tokens)} tokens)")

    # ==================== Token Updates ====================

    def update_color(self, key: str, value: str):
        """
        Update a color token.

        Args:
            key: Color token name (e.g., 'accent_primary', 'bg_primary')
            value: Color value in hex format (e.g., '#00BFFF')
        """
        if hasattr(self.tokens.colors, key):
            setattr(self.tokens.colors, key, value)
            self._customized_tokens.add(f"colors.{key}")
            self._notify_observers()
            logger.debug(f"Updated color.{key} = {value}")
        else:
            logger.warning(f"Unknown color token: {key}")

    def update_typography(self, key: str, value):
        """
        Update a typography token.

        Args:
            key: Typography token name (e.g., 'size_base', 'font_primary')
            value: Typography value
        """
        if hasattr(self.tokens.typography, key):
            setattr(self.tokens.typography, key, value)
            self._customized_tokens.add(f"typography.{key}")
            self._notify_observers()
            logger.debug(f"Updated typography.{key} = {value}")
        else:
            logger.warning(f"Unknown typography token: {key}")

    def update_spacing(self, key: str, value: int):
        """
        Update a spacing token.

        Args:
            key: Spacing token name (e.g., 'base', 'md', 'lg')
            value: Spacing value in pixels
        """
        if hasattr(self.tokens.spacing, key):
            setattr(self.tokens.spacing, key, value)
            self._customized_tokens.add(f"spacing.{key}")
            self._notify_observers()
            logger.debug(f"Updated spacing.{key} = {value}")
        else:
            logger.warning(f"Unknown spacing token: {key}")

    def update_radius(self, key: str, value: int):
        """
        Update a border radius token.

        Args:
            key: Radius token name (e.g., 'base', 'md', 'lg')
            value: Radius value in pixels
        """
        if hasattr(self.tokens.radius, key):
            setattr(self.tokens.radius, key, value)
            self._customized_tokens.add(f"radius.{key}")
            self._notify_observers()
            logger.debug(f"Updated radius.{key} = {value}")
        else:
            logger.warning(f"Unknown radius token: {key}")

    def reset_to_defaults(self):
        """Reset all tokens to default values."""
        logger.info("Resetting theme to defaults")
        self.tokens = OmnixDesignTokens()
        self._customized_tokens.clear()
        self._notify_observers()

    def reset_token(self, category: str, key: str):
        """
        Reset a specific token to its default value.

        Args:
            category: Token category ('colors', 'typography', 'spacing', 'radius')
            key: Token key within category
        """
        # Create temporary default tokens
        defaults = OmnixDesignTokens()

        if category == 'colors' and hasattr(defaults.colors, key):
            default_value = getattr(defaults.colors, key)
            setattr(self.tokens.colors, key, default_value)
            self._customized_tokens.discard(f"colors.{key}")
            self._notify_observers()
            logger.info(f"Reset colors.{key} to default: {default_value}")

        elif category == 'typography' and hasattr(defaults.typography, key):
            default_value = getattr(defaults.typography, key)
            setattr(self.tokens.typography, key, default_value)
            self._customized_tokens.discard(f"typography.{key}")
            self._notify_observers()
            logger.info(f"Reset typography.{key} to default: {default_value}")

        elif category == 'spacing' and hasattr(defaults.spacing, key):
            default_value = getattr(defaults.spacing, key)
            setattr(self.tokens.spacing, key, default_value)
            self._customized_tokens.discard(f"spacing.{key}")
            self._notify_observers()
            logger.info(f"Reset spacing.{key} to default: {default_value}")

        elif category == 'radius' and hasattr(defaults.radius, key):
            default_value = getattr(defaults.radius, key)
            setattr(self.tokens.radius, key, default_value)
            self._customized_tokens.discard(f"radius.{key}")
            self._notify_observers()
            logger.info(f"Reset radius.{key} to default: {default_value}")

        else:
            logger.warning(f"Unknown token: {category}.{key}")

    # ==================== Stylesheet Generation ====================

    def get_stylesheet(self) -> str:
        """
        Generate complete application stylesheet.

        Returns:
            QSS stylesheet string
        """
        return self.design_system.generate_complete_stylesheet()

    def get_overlay_stylesheet(self, opacity: float = 0.75) -> str:
        """
        Generate overlay-specific stylesheet.

        Args:
            opacity: Background opacity (0.0 to 1.0)

        Returns:
            Overlay QSS stylesheet string
        """
        return self.design_system.generate_overlay_stylesheet(opacity)

    # ==================== Observer Pattern ====================

    def add_update_callback(self, callback: Callable):
        """
        Add a callback to be notified when theme changes.

        Args:
            callback: Function to call when theme updates
        """
        if callback not in self._update_callbacks:
            self._update_callbacks.append(callback)
            logger.debug(f"Added theme update callback: {callback.__name__}")

    def remove_update_callback(self, callback: Callable):
        """
        Remove a theme update callback.

        Args:
            callback: Callback function to remove
        """
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)
            logger.debug(f"Removed theme update callback: {callback.__name__}")

    def _notify_observers(self):
        """Notify all observers that theme has changed."""
        for callback in self._update_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in theme update callback {callback.__name__}: {e}")

    # ==================== Utility Methods ====================

    def get_customizations(self) -> Dict[str, Any]:
        """
        Get all customized tokens.

        Returns:
            Dictionary of customized tokens
        """
        customizations = {}

        for token_path in self._customized_tokens:
            category, key = token_path.split('.')
            if category not in customizations:
                customizations[category] = {}

            if category == 'colors':
                customizations[category][key] = getattr(self.tokens.colors, key)
            elif category == 'typography':
                customizations[category][key] = getattr(self.tokens.typography, key)
            elif category == 'spacing':
                customizations[category][key] = getattr(self.tokens.spacing, key)
            elif category == 'radius':
                customizations[category][key] = getattr(self.tokens.radius, key)

        return customizations

    def is_customized(self, category: str, key: str) -> bool:
        """
        Check if a token has been customized.

        Args:
            category: Token category
            key: Token key

        Returns:
            True if token has been customized
        """
        return f"{category}.{key}" in self._customized_tokens

    def get_token_value(self, category: str, key: str) -> Any:
        """
        Get the current value of a token.

        Args:
            category: Token category
            key: Token key

        Returns:
            Token value or None if not found
        """
        if category == 'colors' and hasattr(self.tokens.colors, key):
            return getattr(self.tokens.colors, key)
        elif category == 'typography' and hasattr(self.tokens.typography, key):
            return getattr(self.tokens.typography, key)
        elif category == 'spacing' and hasattr(self.tokens.spacing, key):
            return getattr(self.tokens.spacing, key)
        elif category == 'radius' and hasattr(self.tokens.radius, key):
            return getattr(self.tokens.radius, key)
        return None

    def export_theme(self, filepath: str):
        """
        Export current theme to a file.

        Args:
            filepath: Path to export file
        """
        try:
            theme_data = {
                'version': 2,
                'name': 'Exported Theme',
                'exported': datetime.now().isoformat(),
                'tokens': {
                    'colors': asdict(self.tokens.colors),
                    'typography': asdict(self.tokens.typography),
                    'spacing': asdict(self.tokens.spacing),
                    'radius': asdict(self.tokens.radius),
                }
            }

            with open(filepath, 'w') as f:
                json.dump(theme_data, f, indent=2)

            logger.info(f"Theme exported to {filepath}")

        except Exception as e:
            logger.error(f"Error exporting theme: {e}")

    def import_theme(self, filepath: str):
        """
        Import theme from a file.

        Args:
            filepath: Path to import file
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            if data.get('version') == 2:
                self._load_v2_theme(data)
                self._notify_observers()
                logger.info(f"Theme imported from {filepath}")
            else:
                logger.error(f"Invalid theme file version: {data.get('version')}")

        except Exception as e:
            logger.error(f"Error importing theme: {e}")


# Global singleton instance
_theme_manager_instance: Optional[OmnixThemeManager] = None


def get_theme_manager() -> OmnixThemeManager:
    """
    Get the global theme manager instance (singleton).

    Returns:
        OmnixThemeManager instance
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = OmnixThemeManager()
    return _theme_manager_instance


def initialize_theme_manager(config_dir: str = None) -> OmnixThemeManager:
    """
    Initialize the global theme manager with custom config directory.

    Args:
        config_dir: Configuration directory path

    Returns:
        OmnixThemeManager instance
    """
    global _theme_manager_instance
    _theme_manager_instance = OmnixThemeManager(config_dir=config_dir)
    return _theme_manager_instance
