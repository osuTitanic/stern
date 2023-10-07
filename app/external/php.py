
from typing import Optional

import distutils.spawn
import subprocess
import logging
import json
import os

class PHP:
    """Modified version of php.py (https://github.com/brool/util/blob/master/php.py)"""
    
    def __init__(
        self,
        prefix: str = "",
        postfix: str = "",
        executable_path: Optional[str] = None
    ):
        """
        `prefix`: Optional prefix for all code (usually require statements)\n
        `postfix`: Optional postfix for all code\n
        `executable_path`: Optional path to the php folder (path environment is chosen by default)

        Semicolons are not added automatically, so you'll need to make sure to put them in!
        """

        self.prefix = prefix
        self.postfix = postfix

        if not executable_path:
            executable_path = os.environ["PATH"]

        self.executable_path = distutils.spawn.find_executable("php", executable_path)
        self.logger = logging.getLogger("php")

    def __submit(self, code: str) -> bytes:
        result = subprocess.run(
            [self.executable_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            input=f"<?php {self.prefix} {code} {self.postfix} ?>".encode()
        )

        if result.returncode != 0:
            self.logger.error(result.stderr)
        else:
            self.logger.debug(result.stdout)

        return result.stdout

    def get_raw(self, code: str) -> bytes:
        """Given a code block, invoke the code and return the raw result."""
        out = self.__submit(code)
        return out

    def get(self, code: str) -> dict:
        """Given a code block that emits json, invoke the code and interpret the result as a Python value."""
        out = self.__submit(code)
        return json.loads(out)
