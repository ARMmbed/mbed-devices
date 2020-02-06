# mbed-devices

![Package](https://img.shields.io/badge/Package-mbed--devices-lightgrey)
[![Documentation](https://img.shields.io/badge/Documentation-GitHub_Pages-blue)](https://armmbed.github.io/mbed-devices)
[![PyPI](https://img.shields.io/pypi/v/mbed-devices)](https://pypi.org/project/mbed-devices/)
[![PyPI - Status](https://img.shields.io/pypi/status/mbed-devices)](https://pypi.org/project/mbed-devices/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mbed-devices)](https://pypi.org/project/mbed-devices/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ARMmbed/mbed-devices/blob/master/LICENSE)

[![Build Status](https://dev.azure.com/mbed-tools/mbed-devices/_apis/build/status/Build%20and%20Release?branchName=master)](https://dev.azure.com/mbed-tools/mbed-devices/_build/latest?definitionId=11&branchName=master)
[![Test Coverage](https://codecov.io/gh/ARMmbed/mbed-devices/branch/master/graph/badge.svg)](https://codecov.io/gh/ARMmbed/mbed-devices)
[![Maintainability](https://api.codeclimate.com/v1/badges/08971231f91470bf6d77/maintainability)](https://codeclimate.com/github/ARMmbed/mbed-devices/maintainability)

## Overview

This package provides a way to list devices running Mbed OS connected to the computer this tool is run on.

For a command line interface for Mbed OS please see the package mbed-tools.
## Releases

For release notes and a history of changes of all **production** releases, please see the following:

- [Changelog](https://github.com/ARMmbed/mbed-devices/blob/master/CHANGELOG.md)

For a the list of all available versions please, please see the:

- [PyPI Release History](https://pypi.org/project/mbed-devices/#history)

## Versioning

The version scheme used follows [PEP440](https://www.python.org/dev/peps/pep-0440/) and 
[Semantic Versioning](https://semver.org/). For production quality releases the version will look as follows:

- `<major>.<minor>.<patch>`

Beta releases are used to give early access to new functionality, for testing and to get feedback on experimental 
features. As such these releases may not be stable and should not be used for production. Additionally any interfaces
introduced in a beta release may be removed or changed without notice. For **beta** releases the version will look as
follows:

- `<major>.<minor>.<patch>-beta.<pre-release-number>`

## Installation

It is recommended that a virtual environment such as [Pipenv](https://github.com/pypa/pipenv/blob/master/README.md) is
used for all installations to avoid Python dependency conflicts.

To install the most recent production quality release use:

```
pip install mbed-devices
```

To install a specific release:

```
pip install mbed-devices==<version>
```

## Usage

Interface definition and usage documentation (for developers of Mbed OS tooling) is available for the most recent
production release here:

- [GitHub Pages](https://armmbed.github.io/mbed-devices)

## Project Structure

The follow described the major aspects of the project structure:

- `azure-pipelines/` - CI configuration files for Azure Pipelines.
- `docs/` - Interface definition and usage documentation.
- `examples/` - Usage examples.
- `mbed_devices/` - Python source files.
- `news/` - Collection of news files for unreleased changes.
- `tests/` - Unit and integration tests.

## Getting Help

- For interface definition and usage documentation, please see [GitHub Pages](https://armmbed.github.io/mbed-devices).
- For a list of known issues and possible work arounds, please see [Known Issues](KNOWN_ISSUES.md).
- To raise a defect or enhancement please use [GitHub Issues](https://github.com/ARMmbed/mbed-devices/issues).
- To ask a question please use the [Mbed Forum](https://forums.mbed.com/).

## Contributing

- Mbed OS is an open source project and we are committed to fostering a welcoming community, please see our
  [Code of Conduct](https://github.com/ARMmbed/mbed-devices/blob/master/CODE_OF_CONDUCT.md) for more information.
- For ways to contribute to the project, please see the [Contributions Guidelines](https://github.com/ARMmbed/mbed-devices/blob/master/CONTRIBUTING.md)
- For a technical introduction into developing this package, please see the [Development Guide](https://github.com/ARMmbed/mbed-devices/blob/master/DEVELOPMENT.md)
