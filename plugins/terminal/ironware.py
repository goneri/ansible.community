#
# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import json

from ansible.errors import AnsibleConnectionFailure
from ansible_collections.ansible.community.plugins.module_utils._text import to_text, to_bytes
from ansible.plugins.terminal import TerminalBase


class TerminalModule(TerminalBase):

    terminal_stdout_re = [
        re.compile(br"[\r\n]?(?:\w+@)?[\w+\-\.:\/\[\]]+(?:\([^\)]+\)){,3}(?:>|#) ?$")
    ]

    terminal_stderr_re = [
        re.compile(br"[\r\n]Error - "),
        re.compile(br"[\r\n](?:incomplete|ambiguous|unrecognised|invalid) (?:command|input)", re.I)
    ]

    def on_open_shell(self):
        self.disable_pager()

    def disable_pager(self):
        cmd = {u'command': u'terminal length 0'}
        try:
            self._exec_cli_command(u'terminal length 0')
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure('unable to disable terminal pager')

    def on_become(self, passwd=None):
        if self._get_prompt().strip().endswith(b'#'):
            return

        cmd = {u'command': u'enable'}
        if passwd:
            # Note: python-3.5 cannot combine u"" and r"" together.  Thus make
            # an r string and use to_text to ensure it's text on both py2 and py3.
            cmd[u'prompt'] = to_text(r"[\r\n]?password: ?$", errors='surrogate_or_strict')
            cmd[u'answer'] = passwd

        try:
            self._exec_cli_command(to_bytes(json.dumps(cmd), errors='surrogate_or_strict'))
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure('unable to elevate privilege to enable mode')

    def on_unbecome(self):
        prompt = self._get_prompt()
        if prompt is None:
            # if prompt is None most likely the terminal is hung up at a prompt
            return

        if b'(config' in prompt:
            self._exec_cli_command(b'end')
            self._exec_cli_command(b'exit')

        elif prompt.endswith(b'#'):
            self._exec_cli_command(b'exit')
