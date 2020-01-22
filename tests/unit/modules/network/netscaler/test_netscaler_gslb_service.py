
#  Copyright (c) 2017 Citrix Systems
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

from ansible_collections.ansible.community.tests.unit.compat.mock import patch, Mock, MagicMock, call
from ansible_collections.ansible.community.tests.unit.modules.utils import set_module_args
from ..netscaler_module import TestModule, nitro_base_patcher

import sys

if sys.version_info[:2] != (2, 6):
    import requests


class TestNetscalerGSLBSiteModule(TestModule):

    @classmethod
    def setUpClass(cls):
        class MockException(Exception):
            pass

        cls.MockException = MockException

        m = MagicMock()
        nssrc_modules_mock = {
            'nssrc.com.citrix.netscaler.nitro.resource.config.gslb': m,
            'nssrc.com.citrix.netscaler.nitro.resource.config.gslb.gslbservice': m,
            'nssrc.com.citrix.netscaler.nitro.resource.config.gslb.gslbservice.gslbservice': m,
            'nssrc.com.citrix.netscaler.nitro.resource.config.gslb.gslbservice_lbmonitor_binding': m,
            'nssrc.com.citrix.netscaler.nitro.resource.config.gslb.gslbservice_lbmonitor_binding.gslbservice_lbmonitor_binding': m,

            # The following are needed because of monkey_patch_nitro_api()
            'nssrc.com.citrix.netscaler.nitro.resource.base': m,
            'nssrc.com.citrix.netscaler.nitro.resource.base.Json': m,
            'nssrc.com.citrix.netscaler.nitro.resource.base.Json.Json': m,
            'nssrc.com.citrix.netscaler.nitro.util': m,
            'nssrc.com.citrix.netscaler.nitro.util.nitro_util': m,
            'nssrc.com.citrix.netscaler.nitro.util.nitro_util.nitro_util': m,
        }

        cls.nitro_specific_patcher = patch.dict(sys.modules, nssrc_modules_mock)
        cls.nitro_base_patcher = nitro_base_patcher

    @classmethod
    def tearDownClass(cls):
        cls.nitro_base_patcher.stop()
        cls.nitro_specific_patcher.stop()

    def setUp(self):
        super(TestNetscalerGSLBSiteModule, self).setUp()

        self.nitro_base_patcher.start()
        self.nitro_specific_patcher.start()

        # Setup minimal required arguments to pass AnsibleModule argument parsing

    def tearDown(self):
        super(TestNetscalerGSLBSiteModule, self).tearDown()

        self.nitro_base_patcher.stop()
        self.nitro_specific_patcher.stop()

    def test_graceful_nitro_api_import_error(self):
        # Stop nitro api patching to cause ImportError
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        self.nitro_base_patcher.stop()
        self.nitro_specific_patcher.stop()
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service
        self.module = netscaler_gslb_service
        result = self.failed()
        self.assertEqual(result['msg'], 'Could not load nitro python sdk')

    def test_graceful_nitro_error_on_login(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        class MockException(Exception):
            def __init__(self, *args, **kwargs):
                self.errorcode = 0
                self.message = ''

        client_mock = Mock()
        client_mock.login = Mock(side_effect=MockException)
        m = Mock(return_value=client_mock)
        with patch('ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service.get_nitro_client', m):
            with patch('ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service.nitro_exception', MockException):
                self.module = netscaler_gslb_service
                result = self.failed()
                self.assertTrue(result['msg'].startswith('nitro exception'), msg='nitro exception during login not handled properly')

    def test_graceful_no_connection_error(self):

        if sys.version_info[:2] == (2, 6):
            self.skipTest('requests library not available under python2.6')
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        class MockException(Exception):
            pass
        client_mock = Mock()
        attrs = {'login.side_effect': requests.exceptions.ConnectionError}
        client_mock.configure_mock(**attrs)
        m = Mock(return_value=client_mock)
        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            nitro_exception=MockException,
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertTrue(result['msg'].startswith('Connection error'), msg='Connection error was not handled gracefully')

    def test_graceful_login_error(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        if sys.version_info[:2] == (2, 6):
            self.skipTest('requests library not available under python2.6')

        class MockException(Exception):
            pass
        client_mock = Mock()
        attrs = {'login.side_effect': requests.exceptions.SSLError}
        client_mock.configure_mock(**attrs)
        m = Mock(return_value=client_mock)
        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            monkey_patch_nitro_api=Mock(),
            nitro_exception=MockException,
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertTrue(result['msg'].startswith('SSL Error'), msg='SSL Error was not handled gracefully')

    def test_ensure_feature_is_enabled_called(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        gslb_service_proxy_mock = Mock()
        ensure_feature_is_enabled_mock = Mock()
        client_mock = Mock()

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=Mock(return_value=client_mock),
            gslb_service_exists=Mock(side_effect=[False, True]),
            gslb_service_identical=Mock(side_effect=[True]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=ensure_feature_is_enabled_mock,
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=Mock(return_value=gslb_service_proxy_mock),
        ):
            self.module = netscaler_gslb_service
            self.exited()
            ensure_feature_is_enabled_mock.assert_called_with(client_mock, 'GSLB')

    def test_save_config_called_on_state_present(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        gslb_service_proxy_mock = Mock()

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            gslb_service_exists=Mock(side_effect=[False, True]),
            gslb_service_identical=Mock(side_effect=[True]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=Mock(return_value=gslb_service_proxy_mock),
        ):
            self.module = netscaler_gslb_service
            self.exited()
            self.assertIn(call.save_config(), client_mock.mock_calls)

    def test_save_config_called_on_state_absent(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='absent',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        gslb_service_proxy_mock = Mock()

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            gslb_service_exists=Mock(side_effect=[True, False]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=Mock(return_value=gslb_service_proxy_mock),
        ):
            self.module = netscaler_gslb_service
            self.exited()
            self.assertIn(call.save_config(), client_mock.mock_calls)

    def test_save_config_not_called_on_state_present(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
            save_config=False,
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        gslb_service_proxy_mock = Mock()

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            gslb_service_exists=Mock(side_effect=[False, True]),
            gslb_service_identical=Mock(side_effect=[True]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=Mock(return_value=gslb_service_proxy_mock),
        ):
            self.module = netscaler_gslb_service
            self.exited()
            self.assertNotIn(call.save_config(), client_mock.mock_calls)

    def test_save_config_not_called_on_state_absent(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='absent',
            save_config=False,
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        gslb_service_proxy_mock = Mock()

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            gslb_service_exists=Mock(side_effect=[True, False]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=Mock(return_value=gslb_service_proxy_mock),
        ):
            self.module = netscaler_gslb_service
            self.exited()
            self.assertNotIn(call.save_config(), client_mock.mock_calls)

    def test_new_gslb_site_execution_flow(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            gslb_service_exists=Mock(side_effect=[False, True]),
            gslb_service_identical=Mock(side_effect=[True]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            self.exited()
            gslb_service_proxy_mock.assert_has_calls([call.add()])

    def test_modified_gslb_site_execution_flow(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[True, True]),
            gslb_service_identical=Mock(side_effect=[False, False, True]),
            monitor_bindings_identical=Mock(side_effect=[True, True, True]),
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            nitro_exception=self.MockException,
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            self.exited()
            gslb_service_proxy_mock.assert_has_calls([call.update()])

    def test_absent_gslb_site_execution_flow(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='absent',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[True, False]),
            gslb_service_identical=Mock(side_effect=[False, True]),
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            self.exited()
            gslb_service_proxy_mock.assert_has_calls([call.delete()])

    def test_present_gslb_service_identical_flow(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[True, True]),
            gslb_service_identical=Mock(side_effect=[True, True]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            self.exited()
            gslb_service_proxy_mock.assert_not_called()

    def test_absent_gslb_site_noop_flow(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='absent',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[False, False]),
            gslb_service_identical=Mock(side_effect=[False, False]),
            nitro_exception=self.MockException,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            self.exited()
            gslb_service_proxy_mock.assert_not_called()

    def test_present_gslb_site_failed_update(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            nitro_exception=self.MockException,
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[True, True]),
            gslb_service_identical=Mock(side_effect=[False, False, False]),
            monitor_bindings_identical=Mock(side_effect=[True, True, True]),
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertEqual(result['msg'], 'GSLB service differs from configured')
            self.assertTrue(result['failed'])

    def test_present_gslb_site_failed_monitor_bindings_update(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            nitro_exception=self.MockException,
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[True, True]),
            gslb_service_identical=Mock(side_effect=[False, False, True]),
            monitor_bindings_identical=Mock(side_effect=[False, False, False]),
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertEqual(result['msg'], 'Monitor bindings differ from configured')
            self.assertTrue(result['failed'])

    def test_present_gslb_site_failed_create(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            nitro_exception=self.MockException,
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[False, False]),
            gslb_service_identical=Mock(side_effect=[False, False]),
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertEqual(result['msg'], 'GSLB service does not exist')
            self.assertTrue(result['failed'])

    def test_present_gslb_site_update_immutable_attribute(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            nitro_exception=self.MockException,
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=['domain']),
            gslb_service_exists=Mock(side_effect=[True, True]),
            gslb_service_identical=Mock(side_effect=[False, False]),
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertEqual(result['msg'], 'Cannot update immutable attributes [\'domain\']')
            self.assertTrue(result['failed'])

    def test_absent_gslb_site_failed_delete(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='absent',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        client_mock = Mock()

        m = Mock(return_value=client_mock)

        glsb_service_proxy_attrs = {
            'diff_object.return_value': {},
        }
        gslb_service_proxy_mock = Mock()
        gslb_service_proxy_mock.configure_mock(**glsb_service_proxy_attrs)
        config_proxy_mock = Mock(return_value=gslb_service_proxy_mock)

        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            nitro_exception=self.MockException,
            get_nitro_client=m,
            diff_list=Mock(return_value={}),
            get_immutables_intersection=Mock(return_value=[]),
            gslb_service_exists=Mock(side_effect=[True, True]),
            gslb_service_identical=Mock(side_effect=[False, False]),
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            ConfigProxy=config_proxy_mock,
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertEqual(result['msg'], 'GSLB service still exists')
            self.assertTrue(result['failed'])

    def test_graceful_nitro_exception_state_present(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='present',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        class MockException(Exception):
            def __init__(self, *args, **kwargs):
                self.errorcode = 0
                self.message = ''

        m = Mock(side_effect=MockException)
        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            gslb_service_exists=m,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            nitro_exception=MockException
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertTrue(
                result['msg'].startswith('nitro exception'),
                msg='Nitro exception not caught on operation absent'
            )

    def test_graceful_nitro_exception_state_absent(self):
        set_module_args(dict(
            nitro_user='user',
            nitro_pass='pass',
            nsip='192.0.2.1',
            state='absent',
        ))
        from ansible_collections.ansible.community.plugins.modules import netscaler_gslb_service

        class MockException(Exception):
            def __init__(self, *args, **kwargs):
                self.errorcode = 0
                self.message = ''

        m = Mock(side_effect=MockException)
        with patch.multiple(
            'ansible_collections.ansible.community.plugins.modules.netscaler_gslb_service',
            gslb_service_exists=m,
            ensure_feature_is_enabled=Mock(),
            monkey_patch_nitro_api=Mock(),
            nitro_exception=MockException
        ):
            self.module = netscaler_gslb_service
            result = self.failed()
            self.assertTrue(
                result['msg'].startswith('nitro exception'),
                msg='Nitro exception not caught on operation absent'
            )
