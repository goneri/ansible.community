from ansible_collections.ansible.community.tests.unit.compat import mock
from ansible_collections.ansible.community.tests.unit.compat import unittest

from ansible_collections.ansible.community.plugins.modules import apk


class TestApkQueryLatest(unittest.TestCase):

    def setUp(self):
        self.module_names = [
            'bash',
            'g++',
        ]

    @mock.patch('ansible_collections.ansible.community.plugins.modules.apk.AnsibleModule')
    def test_not_latest(self, mock_module):
        apk.APK_PATH = ""
        for module_name in self.module_names:
            command_output = module_name + '-2.0.0-r1 < 3.0.0-r2 '
            mock_module.run_command.return_value = (0, command_output, None)
            command_result = apk.query_latest(mock_module, module_name)
            self.assertFalse(command_result)

    @mock.patch('ansible_collections.ansible.community.plugins.modules.apk.AnsibleModule')
    def test_latest(self, mock_module):
        apk.APK_PATH = ""
        for module_name in self.module_names:
            command_output = module_name + '-2.0.0-r1 = 2.0.0-r1 '
            mock_module.run_command.return_value = (0, command_output, None)
            command_result = apk.query_latest(mock_module, module_name)
            self.assertTrue(command_result)
