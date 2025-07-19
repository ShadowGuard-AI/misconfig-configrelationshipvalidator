import argparse
import json
import logging
import os
import sys
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Checks for consistency and correctness of relationships between configuration parameters.")
    parser.add_argument("config_files", nargs="+", help="One or more configuration files to validate (YAML or JSON).")
    parser.add_argument("--relationship_file", required=True, help="JSON file defining the relationships to validate.")
    parser.add_argument("--log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level.")
    return parser

def load_config(file_path):
    """
    Loads a configuration file (YAML or JSON).

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: The configuration data as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is not supported or invalid.
    """
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith(('.yaml', '.yml')):
                try:
                    return yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid YAML file: {file_path}. Error: {e}")
            elif file_path.endswith('.json'):
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON file: {file_path}. Error: {e}")
            else:
                raise ValueError("Unsupported file format.  Must be YAML or JSON.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error loading configuration file {file_path}: {e}")

def load_relationships(file_path):
    """
    Loads the relationships file (JSON).

    Args:
        file_path (str): The path to the relationships file.

    Returns:
        dict: The relationships data as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid JSON file.
    """
    try:
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON file: {file_path}. Error: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Relationships file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error loading relationships file {file_path}: {e}")

def validate_relationship(config_data, relationship):
    """
    Validates a single relationship between configuration parameters.

    Args:
        config_data (dict): A dictionary containing all configuration data.
        relationship (dict): A dictionary defining the relationship to validate.

    Returns:
        bool: True if the relationship is valid, False otherwise.
    """
    source_file = relationship.get("source_file")
    source_param = relationship.get("source_param")
    target_file = relationship.get("target_file")
    target_param = relationship.get("target_param")
    comparison = relationship.get("comparison", "equals") # Default comparison is "equals"

    if not all([source_file, source_param, target_file, target_param]):
        logging.error(f"Invalid relationship definition: Missing required fields. Relationship: {relationship}")
        return False

    try:
        source_value = get_value_from_config(config_data, source_file, source_param)
        target_value = get_value_from_config(config_data, target_file, target_param)
    except KeyError as e:
        logging.error(f"Parameter not found: {e} in relationship {relationship}")
        return False

    if source_value is None or target_value is None:
        logging.warning(f"One or more values are None for relationship: {relationship}. Source Value: {source_value}, Target Value: {target_value}")
        return True # Consider None values as valid for now, may want to configure this

    try:
        if comparison == "equals":
            return source_value == target_value
        elif comparison == "not_equals":
            return source_value != target_value
        elif comparison == "greater_than":
            return source_value > target_value
        elif comparison == "less_than":
            return source_value < target_value
        elif comparison == "greater_than_or_equal_to":
            return source_value >= target_value
        elif comparison == "less_than_or_equal_to":
            return source_value <= target_value
        else:
            logging.error(f"Unsupported comparison type: {comparison}")
            return False
    except TypeError:
        logging.error(f"Cannot compare values of different types for relationship: {relationship}")
        return False

def get_value_from_config(config_data, file_name, param_path):
    """
    Retrieves a value from a configuration dictionary using a file name and parameter path.

    Args:
        config_data (dict): The dictionary containing all configuration data.
        file_name (str): The name of the file containing the parameter.
        param_path (str): The path to the parameter within the file, separated by dots (e.g., "service.port").

    Returns:
        The value of the parameter, or None if not found.

    Raises:
        KeyError: If the file or parameter path is not found.
    """
    if file_name not in config_data:
        raise KeyError(f"File '{file_name}' not found in configuration data.")

    data = config_data[file_name]
    path_parts = param_path.split(".")

    try:
        for part in path_parts:
            data = data[part]
        return data
    except KeyError:
        raise KeyError(f"Parameter '{param_path}' not found in file '{file_name}'.")

def main():
    """
    Main function to execute the configuration relationship validation.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        logging.getLogger().setLevel(args.log_level.upper())
    except ValueError:
        print("Invalid log level.  Please choose from DEBUG, INFO, WARNING, ERROR, or CRITICAL.")
        sys.exit(1)

    logging.info("Starting configuration relationship validation...")

    try:
        relationships = load_relationships(args.relationship_file)
    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Failed to load relationships file: {e}")
        sys.exit(1)

    config_data = {}
    for file_path in args.config_files:
        try:
            config_data[os.path.basename(file_path)] = load_config(file_path)
        except (FileNotFoundError, ValueError) as e:
            logging.error(f"Failed to load configuration file {file_path}: {e}")
            sys.exit(1)

    valid = True
    for relationship in relationships:
        if not validate_relationship(config_data, relationship):
            logging.error(f"Relationship validation failed: {relationship}")
            valid = False
        else:
            logging.info(f"Relationship validation passed: {relationship}")

    if valid:
        logging.info("All relationships validated successfully.")
        sys.exit(0)
    else:
        logging.error("One or more relationship validations failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()