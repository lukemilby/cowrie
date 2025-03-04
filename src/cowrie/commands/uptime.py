# Copyright (c) 2009 Upi Tamminen <desaster@gmail.com>
# See the COPYRIGHT file for more information


import time

from cowrie.core import utils
from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_uptime(HoneyPotCommand):
    def call(self):
        self.write(
            "%s  up %s,  1 user,  load average: 0.00, 0.00, 0.00\n"
            % (time.strftime("%H:%M:%S"), utils.uptime(self.protocol.uptime()))
        )


commands["/usr/bin/uptime"] = Command_uptime
commands["uptime"] = Command_uptime
