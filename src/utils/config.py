"""
Configuration management for the PDF converter.

Handles loading settings from YAML files and merging them with
command-line arguments to provide a unified configuration.
"""

import yaml
import argparse
from typing import Dict, Any, Optional

DEFAULT_CONFIG_PATH = "config.yaml"


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads configuration from a YAML file.

    Args:
        config_path: The path to the YAML configuration file. If not provided,
                     it defaults to 'config.yaml' in the current directory.

    Returns:
        A dictionary containing the loaded configuration, or an empty dictionary
        if the file is not found.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at '{config_path}'. Using default settings.")
        return {}
    except Exception as e:
        print(f"Error loading configuration from '{config_path}': {e}")
        return {}


def merge_configs(base_config: Dict[str, Any], *extra_configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges multiple configuration dictionaries recursively.

    Args:
        base_config: The base configuration dictionary.
        *extra_configs: Additional configuration dictionaries to merge on top.

    Returns:
        The merged configuration dictionary.
    """
    merged = base_config.copy()
    for config in extra_configs:
        for key, value in config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = merge_configs(merged[key], value)
            else:
                merged[key] = value
    return merged


def get_final_config(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Constructs the final configuration by merging defaults, YAML file, and command-line arguments.

    The priority for settings is:
    1. Command-line arguments (if provided and not default).
    2. Settings from the YAML configuration file.
    3. Default values defined in the configuration structure.

    Args:
        args: The parsed command-line arguments from argparse.

    Returns:
        A dictionary representing the final, unified configuration.
    """
    # Load configuration from the specified YAML file
    yaml_config = load_config(getattr(args, 'config', DEFAULT_CONFIG_PATH))

    # Prepare configuration from command-line arguments, excluding None values
    cli_config = {
        'conversion': {
            'dpi': getattr(args, 'dpi', None),
            'jpeg_quality': getattr(args, 'quality', None),
        },
        'sample': {
            'output_dir': getattr(args, 'sample_dir', None),
            'page': getattr(args, 'sample_page', None),
        },
        'batch': {
            'recursive': getattr(args, 'recursive', None),
            'pattern': getattr(args, 'pattern', None),
            'skip_existing': getattr(args, 'skip_existing', None),
        }
    }

    # Filter out None values from cli_config to avoid overwriting valid settings
    # with non-provided command-line options.
    filtered_cli_config = {
        section: {key: value for key, value in settings.items() if value is not None}
        for section, settings in cli_config.items()
    }

    # Merge configurations with the correct priority
    # Command-line arguments (filtered) > YAML file > Default values (already in yaml_config)
    final_config = merge_configs(yaml_config, filtered_cli_config)

    return final_config
