#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) Philipp Joos 2017
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

DOCUMENTATION = '''
---
module: foreman_compute_profile
short_description: Manage Foreman Compute Profiles using Foreman API
description:
  - Create and delete Foreman Compute Profiles using Foreman API
version_added: "2.0"
author: "Philipp Joos (@philippj)"
requirements:
  - "nailgun >= 0.28.0"
  - "python >= 2.6"
  - "ansible >= 2.3"
options:
  name:
    description: compute profile name
    required: true
  updated_name:
    description: new compute profile name
    required: false
  server_url:
    description: foreman url
    required: true
  username:
    description: foreman username
    required: true
  password:
    description: foreman user password
    required: true
  verify_ssl:
    description: verify ssl connection when communicating with foreman
    default: true
    type: bool
  state:
    description: compute profile presence
    default: present
    choices: ["present", "absent"]
'''

EXAMPLES = '''
- name: compute profile
  foreman_compute_profile:
    name: example_compute_profile
    server_url: foreman.example.com
    username: admin
    password: secret
    verify_ssl: false
    state: present
'''

RETURN = ''' # '''

try:
    import nailgun.entities
    import ansible.module_utils.ansible_nailgun_cement as cement
    has_import_error = False

except ImportError as e:
    has_import_error = True
    import_error_msg = str(e)

from ansible.module_utils.basic import AnsibleModule


# This is the only true source for names (and conversions thereof)
name_map = {
    'name': 'name',
}


def main(module):
    if has_import_error:
        module.fail_json(msg=import_error_msg)

    updated_name = module.params.get('updated_name')
    state = module.params.get('state')

    cement.create_server(
        server_url=module.params.get('server_url'),
        auth=(module.params.get('username'), module.params.get('password')),
        verify_ssl=module.params.get('verify_ssl'),
    )

    cement.ping_server(module)

    data = {
        'name': module.params.get('name')
    }

    compute_profile = cement.find_compute_profile(module, name=data.get('name'), failsafe=True)

    if state == 'present' and updated_name:
        data['name'] = updated_name

    data = cement.sanitize_entity_dict(data, name_map)

    changed = cement.naildown_entity_state(nailgun.entities.ComputeProfile, data, compute_profile, state, module)

    return changed


if __name__ == '__main__':
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            updated_name=dict(),
            server_url=dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            verify_ssl=dict(type='bool', default=True),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True,
    )
    changed = main(module)
    module.exit_json(changed=changed)
