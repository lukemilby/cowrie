# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.

"""
This module contains the sleep command
"""


import re

from twisted.internet import reactor  # type: ignore

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_sleep(HoneyPotCommand):
    """
    Sleep
    """

    pattern = re.compile(r"(\d+)[mhs]?")

    def done(self):
        self.exit()

    def start(self):
        if len(self.args) == 1:
            m = re.match(r"(\d+)[mhs]?", self.args[0])
            if m:
                _time = int(m.group(1))
                # Always sleep in seconds, not minutes or hours
                self.scheduled = reactor.callLater(_time, self.done)
            else:
                self.write("usage: sleep seconds\n")
                self.exit()
        else:
            self.write("usage: sleep seconds\n")
            self.exit()


commands["/bin/sleep"] = Command_sleep
commands["sleep"] = Command_sleep
