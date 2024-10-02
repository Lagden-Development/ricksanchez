"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This script handles the configuration setup for the bot, ensuring that the config file is available
and correctly loaded. It uses the `configparser` module to manage these configurations.

The script checks for the existence of main and custom configuration files, reads them, and initializes parsers
to manage configuration data. If any configuration files are missing, it either logs a warning or creates a basic
custom configuration file.
"""

# Import the required modules

# Python Standard Library
import os  # os is used for interacting with the file system, checking the existence of files, and handling file operations.
import configparser  # configparser is used to parse and manage configuration files in the INI format.

# Internal Helpers
from helpers.logs import (
    RICKLOG_MAIN,
)  # Importing a logging utility from the helpers.logs module to log messages regarding the configuration process.

# Initialize config parsers
# -------------------------
# CONFIG will handle the main configuration, while CUSTOM_CONFIG will manage any custom settings.
# These ConfigParser instances will store and manage the configuration data read from the files.
CONFIG = configparser.ConfigParser()
CUSTOM_CONFIG = configparser.ConfigParser()

# Ensure the config file exists
# -----------------------------
# Check if the main configuration file "config.ini" exists in the current directory.
# If it doesn't exist, the script logs a warning and exits, as the bot cannot function without this core configuration.
if not os.path.exists("config.ini"):
    RICKLOG_MAIN.warning("Config file not found, exiting.")
    exit(1)  # Exit the script with a status code of 1 to indicate an error condition.

# Read the config file
# --------------------
# Load the configuration from "config.ini" into the CONFIG parser.
# The read method loads the contents of the file, allowing subsequent code to access the configuration settings.
CONFIG.read("config.ini")
