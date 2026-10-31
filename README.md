![Banner](banner.png)

# misconfig-ConfigRelationshipValidator
Checks for consistency and correctness of relationships defined between configuration parameters. For example, verifying that the 'port' value in one service configuration matches the 'listening_port' in another service's configuration if they are supposed to communicate. - Focused on Check for misconfigurations in configuration files or infrastructure definitions

A relationship that touches a value that is present but empty (null in YAML, None) fails at exit 1. An empty setting is not treated as passing a comparison that never took place. Two supplied config files that share the same base name are refused at exit 1, naming both paths, because config files are keyed by base name and one would otherwise silently replace the other.

## Install
`git clone https://github.com/ShadowGuardAI/misconfig-configrelationshipvalidator`
`pip install -r requirements.txt`

## Usage
`python3 main.py config_files --relationship_file RELATIONSHIP_FILE [--log_level LOG_LEVEL]`

## Relationships file format
The relationships file is a JSON array of objects. Each object names `source_file` and `target_file` (the base names of two of the supplied config files), `source_param` and `target_param` (dotted paths through mappings, for example `service.port`), and an optional `comparison`, one of `equals` (the default), `not_equals`, `greater_than`, `less_than`, `greater_than_or_equal_to`, or `less_than_or_equal_to`. An empty array, or a file that is not a JSON array of objects, is a load error and exits 1: no relationships would be checked, so no config is reported valid. A malformed relationship, or a dotted path that crosses a non-mapping value, is reported as a failed relationship at exit 1 and the remaining relationships are still checked.

## Parameters
- `config_files`: One or more configuration files to validate (YAML or JSON) (required positional).
- `-h, --help`: Show help message and exit
- `--relationship_file`: JSON file defining the relationships to validate (required).
- `--log_level`: Set the logging level. One of DEBUG, INFO, WARNING, ERROR, CRITICAL (default INFO).

## License
Copyright (c) ShadowGuardAI
