"""
Macro AI Generator Module
Generates and refines macros using AI from natural language descriptions
"""

import json
import logging
from typing import List, Optional, Tuple

from macro_manager import Macro, MacroStep, MacroStepType

logger = logging.getLogger(__name__)


class MacroAIGenerator:
    """
    Generates macros from natural language using AI
    Validates generated macros and provides refinement capabilities
    """

    def __init__(self, ai_router):
        """
        Initialize the AI generator

        Args:
            ai_router: AIRouter instance for API calls
        """
        self.ai_router = ai_router

        # JSON schema for strict macro format
        self.macro_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Macro name"},
                "description": {"type": "string", "description": "Macro description"},
                "repeat": {"type": "integer", "minimum": 1, "description": "Number of repetitions"},
                "randomize_delay": {"type": "boolean", "description": "Add random jitter"},
                "delay_jitter_ms": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Max jitter in ms",
                },
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": [
                                    "key_press",
                                    "key_down",
                                    "key_up",
                                    "key_sequence",
                                    "mouse_move",
                                    "mouse_click",
                                    "mouse_scroll",
                                    "delay",
                                ],
                            },
                            "key": {"type": ["string", "null"]},
                            "button": {"type": ["string", "null"]},
                            "x": {"type": ["integer", "null"]},
                            "y": {"type": ["integer", "null"]},
                            "scroll_amount": {"type": "integer"},
                            "duration_ms": {"type": "integer", "minimum": 0},
                            "delay_jitter_ms": {"type": "integer", "minimum": 0},
                        },
                        "required": ["type"],
                    },
                },
            },
            "required": ["name", "description", "steps"],
        }

    def generate_macro(
        self, description: str, game_name: str = "Unknown"
    ) -> Tuple[Optional[Macro], str]:
        """
        Generate a macro from natural language description

        Args:
            description: Natural language description of the macro
            game_name: Name of the game (for context)

        Returns:
            Tuple of (Macro or None, error_message or success_message)
        """
        try:
            # Create prompt for AI
            prompt = self._create_generation_prompt(description, game_name)

            # Get AI response
            logger.debug(f"Requesting macro generation from AI: {description}")
            response = self.ai_router.chat(
                [{"role": "user", "content": prompt}], model=None  # Use default model
            )

            # Extract JSON from response
            macro_data = self._extract_json_from_response(response)

            if not macro_data:
                return (
                    None,
                    "❌ Failed to extract macro data from AI response. Please try a different description.",
                )

            # Validate the generated macro
            is_valid, errors = self._validate_macro_data(macro_data)
            if not is_valid:
                error_list = "\n".join(f"  • {e}" for e in errors)
                return None, f"❌ Generated macro has errors:\n{error_list}"

            # Convert to Macro object
            macro = self._convert_to_macro(macro_data)
            return macro, "✅ Macro generated successfully!"

        except Exception as e:
            logger.error(f"Error generating macro: {e}")
            return None, f"❌ Error generating macro: {str(e)}"

    def refine_macro(self, macro: Macro, instruction: str) -> Tuple[Optional[Macro], str]:
        """
        Refine an existing macro with AI

        Args:
            macro: Existing Macro to refine
            instruction: Refinement instruction (e.g., "make it slower", "add a pause at the end")

        Returns:
            Tuple of (Refined Macro or None, error_message or success_message)
        """
        try:
            # Create prompt for refinement
            prompt = self._create_refinement_prompt(macro, instruction)

            # Get AI response
            logger.debug(f"Requesting macro refinement from AI: {instruction}")
            response = self.ai_router.chat([{"role": "user", "content": prompt}], model=None)

            # Extract JSON from response
            macro_data = self._extract_json_from_response(response)

            if not macro_data:
                return None, "❌ Failed to extract refined macro from AI response."

            # Validate the refined macro
            is_valid, errors = self._validate_macro_data(macro_data)
            if not is_valid:
                error_list = "\n".join(f"  • {e}" for e in errors)
                return None, f"❌ Refined macro has errors:\n{error_list}"

            # Convert to Macro object, preserving ID
            refined_macro = self._convert_to_macro(macro_data)
            refined_macro.id = macro.id  # Keep original ID
            refined_macro.created_at = macro.created_at  # Keep original creation time

            return refined_macro, "✅ Macro refined successfully!"

        except Exception as e:
            logger.error(f"Error refining macro: {e}")
            return None, f"❌ Error refining macro: {str(e)}"

    def _create_generation_prompt(self, description: str, game_name: str) -> str:
        """Create prompt for macro generation"""
        return f"""You are a gaming macro expert. Generate a macro that performs this action:

"{description}"

Context: Game = {game_name}

Return ONLY a valid JSON object (no markdown, no backticks, just raw JSON) with this structure:
{{
    "name": "short macro name",
    "description": "what this macro does",
    "repeat": 1,
    "randomize_delay": false,
    "delay_jitter_ms": 0,
    "steps": [
        {{"type": "key_press", "key": "1"}},
        {{"type": "delay", "duration_ms": 100}},
        {{"type": "key_press", "key": "2"}},
        {{"type": "mouse_click", "button": "left", "x": 500, "y": 400}},
        {{"type": "delay", "duration_ms": 200}}
    ]
}}

Common keys: a-z, 0-9, space, enter, shift, ctrl, alt
Mouse buttons: left, right, middle
Step types: key_press, key_down, key_up, key_sequence, mouse_move, mouse_click, mouse_scroll, delay

IMPORTANT: Return ONLY the JSON object, nothing else."""

    def _create_refinement_prompt(self, macro: Macro, instruction: str) -> str:
        """Create prompt for macro refinement"""
        macro_json = json.dumps(macro.to_dict(), indent=2)

        return f"""You are a gaming macro expert. Refine this macro:

{macro_json}

Refinement instruction: "{instruction}"

Return ONLY the modified JSON object (no markdown, no backticks, just raw JSON).
Apply the refinement while keeping the macro's core functionality.

IMPORTANT: Return ONLY the JSON object, nothing else."""

    def _extract_json_from_response(self, response: str) -> Optional[dict]:
        """
        Extract JSON from AI response

        Args:
            response: Raw AI response text

        Returns:
            Parsed JSON dict or None
        """
        try:
            # Try to find JSON in response
            # First try direct parsing
            try:
                return json.loads(response.strip())
            except json.JSONDecodeError:
                pass

            # Try removing markdown code blocks
            if "```json" in response:
                json_text = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_text)

            if "```" in response:
                json_text = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_text)

            # Try to find JSON object in response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            logger.warning(f"Could not extract JSON from response: {response[:200]}")
            return None

        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return None

    def _validate_macro_data(self, macro_data: dict) -> Tuple[bool, List[str]]:
        """
        Validate macro data structure

        Args:
            macro_data: Dictionary to validate

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        # Check required fields
        if "name" not in macro_data or not macro_data.get("name"):
            errors.append("Missing or empty 'name' field")

        if "description" not in macro_data:
            errors.append("Missing 'description' field")

        if "steps" not in macro_data or not isinstance(macro_data.get("steps"), list):
            errors.append("Missing or invalid 'steps' field")

        if len(macro_data.get("steps", [])) == 0:
            errors.append("Macro must have at least one step")

        # Validate steps
        valid_types = [e.value for e in MacroStepType]
        for i, step in enumerate(macro_data.get("steps", [])):
            if "type" not in step:
                errors.append(f"Step {i+1}: Missing 'type' field")
                continue

            if step["type"] not in valid_types:
                errors.append(f"Step {i+1}: Invalid type '{step['type']}'")

            # Validate step-specific fields
            if step["type"] in ["key_press", "key_down", "key_up"]:
                if not step.get("key"):
                    errors.append(f"Step {i+1}: Key steps require 'key' field")

            if step["type"] == "mouse_click":
                if step.get("button") not in ["left", "right", "middle"]:
                    errors.append(f"Step {i+1}: Invalid button '{step.get('button')}'")

        return len(errors) == 0, errors

    def _convert_to_macro(self, macro_data: dict) -> Macro:
        """
        Convert validated macro data to Macro object

        Args:
            macro_data: Dictionary with macro data

        Returns:
            Macro object
        """
        import uuid

        # Create steps
        steps = []
        for step_data in macro_data.get("steps", []):
            step = MacroStep(
                type=step_data.get("type", "delay"),
                key=step_data.get("key"),
                duration_ms=step_data.get("duration_ms", 0),
                button=step_data.get("button"),
                x=step_data.get("x"),
                y=step_data.get("y"),
                scroll_amount=step_data.get("scroll_amount", 0),
                meta=step_data.get("meta", {}),
                delay_jitter_ms=step_data.get("delay_jitter_ms", 0),
            )
            steps.append(step)

        # Create macro
        macro = Macro(
            id=str(uuid.uuid4()),
            name=macro_data.get("name", "Generated Macro"),
            description=macro_data.get("description", ""),
            steps=steps,
            game_profile_id=None,
            repeat=macro_data.get("repeat", 1),
            randomize_delay=macro_data.get("randomize_delay", False),
            delay_jitter_ms=macro_data.get("delay_jitter_ms", 0),
            enabled=True,
        )

        return macro

    def get_example_macros(self) -> str:
        """Get example macros for user reference"""
        examples = [
            {
                "name": "Quick Attack",
                "description": "Press 1 then 2 quickly",
                "steps": [
                    {"type": "key_press", "key": "1"},
                    {"type": "delay", "duration_ms": 100},
                    {"type": "key_press", "key": "2"},
                ],
            },
            {
                "name": "Dodge Sequence",
                "description": "Press spacebar then press space again after delay",
                "steps": [
                    {"type": "key_press", "key": "space"},
                    {"type": "delay", "duration_ms": 200},
                    {"type": "key_press", "key": "space"},
                ],
            },
            {
                "name": "Click Coordinates",
                "description": "Move mouse and click",
                "steps": [
                    {"type": "mouse_move", "x": 500, "y": 400},
                    {"type": "delay", "duration_ms": 100},
                    {"type": "mouse_click", "button": "left"},
                ],
            },
        ]

        return json.dumps(examples, indent=2)
