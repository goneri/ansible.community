# -*- coding: utf-8 -*-
#
# Copyright: (c) 2018, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
import sys

if sys.version_info < (2, 7):
    pytestmark = pytest.mark.skip("F5 Ansible modules require Python >= 2.7")

from ansible_collections.ansible.community.plugins.module_utils.basic import AnsibleModule

try:
    from library.modules.bigip_profile_server_ssl import ApiParameters
    from library.modules.bigip_profile_server_ssl import ModuleParameters
    from library.modules.bigip_profile_server_ssl import ModuleManager
    from library.modules.bigip_profile_server_ssl import ArgumentSpec

    # In Ansible 2.8, Ansible changed import paths.
    from test.units.compat import unittest
    from test.units.compat.mock import Mock

    from test.units.modules.utils import set_module_args
except ImportError:
    from ansible_collections.ansible.community.plugins.modules.bigip_profile_server_ssl import ApiParameters
    from ansible_collections.ansible.community.plugins.modules.bigip_profile_server_ssl import ModuleParameters
    from ansible_collections.ansible.community.plugins.modules.bigip_profile_server_ssl import ModuleManager
    from ansible_collections.ansible.community.plugins.modules.bigip_profile_server_ssl import ArgumentSpec

    # Ansible 2.8 imports
    from ansible_collections.ansible.community.tests.unit.compat import unittest
    from ansible_collections.ansible.community.tests.unit.compat.mock import Mock

    from ansible_collections.ansible.community.tests.unit.modules.utils import set_module_args


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            name='foo',
            server_name='foo.bar.com',
            secure_renegotiation='require',
        )

        p = ModuleParameters(params=args)
        assert p.name == 'foo'
        assert p.server_name == 'foo.bar.com'
        assert p.secure_renegotiation == 'require'

    def test_api_parameters(self):
        args = load_fixture('load_ltm_profile_serverssl_1.json')
        p = ApiParameters(params=args)
        assert p.name == 'asda'
        assert p.server_name is None


class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()

    def test_create(self, *args):
        # Configure the arguments that would be sent to the Ansible module
        set_module_args(dict(
            name='foo',
            server_name='foo.bar.com',
            provider=dict(
                server='localhost',
                password='password',
                user='admin'
            )
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
            required_together=self.spec.required_together
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.exists = Mock(return_value=False)
        mm.create_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
