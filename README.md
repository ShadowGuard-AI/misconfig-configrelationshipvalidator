# misconfig-ConfigRelationshipValidator
Checks for consistency and correctness of relationships defined between configuration parameters. For example, verifying that the 'port' value in one service configuration matches the 'listening_port' in another service's configuration if they are supposed to communicate. - Focused on Check for misconfigurations in configuration files or infrastructure definitions

## Install
`git clone https://github.com/ShadowGuardAI/misconfig-configrelationshipvalidator`

## Usage
`./misconfig-configrelationshipvalidator [params]`

## Parameters
- `-h`: Show help message and exit
- `--relationship_file`: JSON file defining the relationships to validate.
- `--log_level`: Set the logging level.

## License
Copyright (c) ShadowGuardAI
