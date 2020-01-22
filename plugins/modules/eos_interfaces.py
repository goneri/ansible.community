#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

##############################################
#                 WARNING                    #
##############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
##############################################

"""
The module file for eos_interfaces
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}


DOCUMENTATION = '''
---
module: eos_interfaces
short_description: Manages interface attributes of Arista EOS interfaces
description: ['This module manages the interface attributes of Arista EOS interfaces.']
author: ['Nathaniel Case (@qalthos)']
notes:
- Tested against Arista EOS 4.20.10M
- This module works with connection C(network_cli). See the
  L(EOS Platform Options,../network/user_guide/platform_eos.html).
options:
  config:
    description: The provided configuration
    type: list
    suboptions:
      name:
        description:
        - Full name of the interface, e.g. GigabitEthernet1.
        type: str
        required: true
      description:
        description:
        - Interface description
        type: str
      duplex:
        description:
        - Interface link status. Applicable for Ethernet interfaces only.
        - Values other than C(auto) must also set I(speed).
        - Ignored when I(speed) is set above C(1000).
        type: str
      enabled:
        default: true
        description:
        - Administrative state of the interface.
        - Set the value to C(true) to administratively enable the interface or C(false)
          to disable it.
        type: bool
      mtu:
        description:
        - MTU for a specific interface. Must be an even number between 576 and 9216.
          Applicable for Ethernet interfaces only.
        type: int
      speed:
        description:
        - Interface link speed. Applicable for Ethernet interfaces only.
        type: str
  state:
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    default: merged
    description:
    - The state of the configuration after module completion.
    type: str

'''

EXAMPLES = """
---

# Using merged

# Before state:
# -------------
#
# veos#show running-config | section interface
# interface Ethernet1
#    description "Interface 1"
# !
# interface Ethernet2
# !
# interface Management1
#    description "Management interface"
#    ip address dhcp
# !

- name: Merge provided configuration with device configuration
  eos_interfaces:
    config:
      - name: Ethernet1
        enabled: True
      - name: Ethernet2
        description: 'Configured by Ansible'
        enabled: False
    state: merged

# After state:
# ------------
#
# veos#show running-config | section interface
# interface Ethernet1
#    description "Interface 1"
# !
# interface Ethernet2
#    description "Configured by Ansible"
#    shutdown
# !
# interface Management1
#    description "Management interface"
#    ip address dhcp
# !

# Using replaced

# Before state:
# -------------
#
# veos#show running-config | section interface
# interface Ethernet1
#    description "Interface 1"
# !
# interface Ethernet2
# !
# interface Management1
#    description "Management interface"
#    ip address dhcp
# !

- name: Replaces device configuration of listed interfaces with provided configuration
  eos_interfaces:
    config:
      - name: Ethernet1
        enabled: True
      - name: Ethernet2
        description: 'Configured by Ansible'
        enabled: False
    state: replaced

# After state:
# ------------
#
# veos#show running-config | section interface
# interface Ethernet1
# !
# interface Ethernet2
#    description "Configured by Ansible"
#    shutdown
# !
# interface Management1
#    description "Management interface"
#    ip address dhcp
# !

# Using overridden

# Before state:
# -------------
#
# veos#show running-config | section interface
# interface Ethernet1
#    description "Interface 1"
# !
# interface Ethernet2
# !
# interface Management1
#    description "Management interface"
#    ip address dhcp
# !

- name: Overrides all device configuration with provided configuration
  eos_interfaces:
    config:
      - name: Ethernet1
        enabled: True
      - name: Ethernet2
        description: 'Configured by Ansible'
        enabled: False
    state: overridden

# After state:
# ------------
#
# veos#show running-config | section interface
# interface Ethernet1
# !
# interface Ethernet2
#    description "Configured by Ansible"
#    shutdown
# !
# interface Management1
#    ip address dhcp
# !

# Using deleted

# Before state:
# -------------
#
# veos#show running-config | section interface
# interface Ethernet1
#    description "Interface 1"
# !
# interface Ethernet2
# !
# interface Management1
#    description "Management interface"
#    ip address dhcp
# !

- name: Delete or return interface parameters to default settings
  eos_interfaces:
    config:
      - name: Ethernet1
    state: deleted

# After state:
# ------------
#
# veos#show running-config | section interface
# interface Ethernet1
# !
# interface Ethernet2
# !
# interface Management1
#    description "Management interface"
#    ip address dhcp
# !
"""

RETURN = """
before:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: dict
  sample: The configuration returned will always be in the same format of the parameters above.
after:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: dict
  sample: The configuration returned will always be in the same format of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['interface Ethernet2', 'shutdown', 'speed 10full']
"""


from ansible_collections.ansible.community.plugins.module_utils.basic import AnsibleModule
from ansible_collections.ansible.community.plugins.module_utils.network.eos.argspec.interfaces.interfaces import InterfacesArgs
from ansible_collections.ansible.community.plugins.module_utils.network.eos.config.interfaces.interfaces import Interfaces


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=InterfacesArgs.argument_spec,
                           supports_check_mode=True)

    result = Interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
