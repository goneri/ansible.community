# Copyright 2019 Fortinet, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <https://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
from mock import ANY
from ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios import FortiOSHandler

try:
    from ansible_collections.ansible.community.plugins.modules import fortios_system_management_tunnel
except ImportError:
    pytest.skip("Could not load required modules for testing", allow_module_level=True)


@pytest.fixture(autouse=True)
def connection_mock(mocker):
    connection_class_mock = mocker.patch('ansible_collections.ansible.community.plugins.modules.fortios_system_management_tunnel.Connection')
    return connection_class_mock


fos_instance = FortiOSHandler(connection_mock)


def test_system_management_tunnel_creation(mocker):
    schema_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'success', 'http_method': 'POST', 'http_status': 200}
    set_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'system_management_tunnel': {
            'allow_collect_statistics': 'enable',
            'allow_config_restore': 'enable',
            'allow_push_configuration': 'enable',
            'allow_push_firmware': 'enable',
            'authorized_manager_only': 'enable',
            'serial_number': 'test_value_8',
            'status': 'enable'
        },
        'vdom': 'root'}

    is_error, changed, response = fortios_system_management_tunnel.fortios_system(input_data, fos_instance)

    expected_data = {
        'allow-collect-statistics': 'enable',
        'allow-config-restore': 'enable',
        'allow-push-configuration': 'enable',
        'allow-push-firmware': 'enable',
        'authorized-manager-only': 'enable',
        'serial-number': 'test_value_8',
        'status': 'enable'
    }

    set_method_mock.assert_called_with('system', 'management-tunnel', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert not is_error
    assert changed
    assert response['status'] == 'success'
    assert response['http_status'] == 200


def test_system_management_tunnel_creation_fails(mocker):
    schema_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'error', 'http_method': 'POST', 'http_status': 500}
    set_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'system_management_tunnel': {
            'allow_collect_statistics': 'enable',
            'allow_config_restore': 'enable',
            'allow_push_configuration': 'enable',
            'allow_push_firmware': 'enable',
            'authorized_manager_only': 'enable',
            'serial_number': 'test_value_8',
            'status': 'enable'
        },
        'vdom': 'root'}

    is_error, changed, response = fortios_system_management_tunnel.fortios_system(input_data, fos_instance)

    expected_data = {
        'allow-collect-statistics': 'enable',
        'allow-config-restore': 'enable',
        'allow-push-configuration': 'enable',
        'allow-push-firmware': 'enable',
        'authorized-manager-only': 'enable',
        'serial-number': 'test_value_8',
        'status': 'enable'
    }

    set_method_mock.assert_called_with('system', 'management-tunnel', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert is_error
    assert not changed
    assert response['status'] == 'error'
    assert response['http_status'] == 500


def test_system_management_tunnel_idempotent(mocker):
    schema_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'error', 'http_method': 'DELETE', 'http_status': 404}
    set_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'system_management_tunnel': {
            'allow_collect_statistics': 'enable',
            'allow_config_restore': 'enable',
            'allow_push_configuration': 'enable',
            'allow_push_firmware': 'enable',
            'authorized_manager_only': 'enable',
            'serial_number': 'test_value_8',
            'status': 'enable'
        },
        'vdom': 'root'}

    is_error, changed, response = fortios_system_management_tunnel.fortios_system(input_data, fos_instance)

    expected_data = {
        'allow-collect-statistics': 'enable',
        'allow-config-restore': 'enable',
        'allow-push-configuration': 'enable',
        'allow-push-firmware': 'enable',
        'authorized-manager-only': 'enable',
        'serial-number': 'test_value_8',
        'status': 'enable'
    }

    set_method_mock.assert_called_with('system', 'management-tunnel', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert not is_error
    assert not changed
    assert response['status'] == 'error'
    assert response['http_status'] == 404


def test_system_management_tunnel_filter_foreign_attributes(mocker):
    schema_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'success', 'http_method': 'POST', 'http_status': 200}
    set_method_mock = mocker.patch('ansible_collections.ansible.community.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'system_management_tunnel': {
            'random_attribute_not_valid': 'tag',
            'allow_collect_statistics': 'enable',
            'allow_config_restore': 'enable',
            'allow_push_configuration': 'enable',
            'allow_push_firmware': 'enable',
            'authorized_manager_only': 'enable',
            'serial_number': 'test_value_8',
            'status': 'enable'
        },
        'vdom': 'root'}

    is_error, changed, response = fortios_system_management_tunnel.fortios_system(input_data, fos_instance)

    expected_data = {
        'allow-collect-statistics': 'enable',
        'allow-config-restore': 'enable',
        'allow-push-configuration': 'enable',
        'allow-push-firmware': 'enable',
        'authorized-manager-only': 'enable',
        'serial-number': 'test_value_8',
        'status': 'enable'
    }

    set_method_mock.assert_called_with('system', 'management-tunnel', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert not is_error
    assert changed
    assert response['status'] == 'success'
    assert response['http_status'] == 200
