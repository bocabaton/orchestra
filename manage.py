#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    from pyengine import settings
    settings.LOGGING_CONFIG = None

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyengine.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
