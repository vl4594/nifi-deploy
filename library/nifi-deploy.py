#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, [New Contributor(s)]
# Copyright: (c) 2015, [Original Contributor(s)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: nifi-deploy
short_description: Deploy and instantiate Apache NiFi template
description:
    - Upload and instantiate NiFi processor group template 
version_added: "0.1"
ANSIBLE_METADATA = {'metadata_version': '1.1',
'status': ['preview'], 'supported_by': 'community'}
'''

EXAMPLES = '''
'''
import requests
import time
import xml.etree.ElementTree as ET
from ansible.module_utils.basic import *



# get template name from template file
def get_template_name(module):
    template_file = module.params['template_file']
    if not template_file:
        module.fail_json(msg="template_file is required")
    try:
        tree = ET.parse(template_file)
        root = tree.getroot()
        for child in root:
            if (child.tag == 'name'):
                module.params['template_name']=child.text
                return child.text
    except IOError:
        module.fail_json(msg="get_template_name: unable to find %s" % template_file)
    except ET.ParseError as e:
        module.fail_json(msg="get_template_name parse error in %s: %s" % (template_file, str(e)))

# deploy template to flow
def instantiate_template(module):
    nifi_url = module.params['nifi_url']
    if not nifi_url:
        module.fail_json(msg="add_template: unable to get nifi_url from module.params")
    template_id = module.params['template_id']
    if not template_id:
        module.fail_json(msg="add_template: unable to get template_id from module.params")
    parent_id = module.params['parent_id']
    if not parent_id:
        module.fail_json(msg="upload: unable to get parent_id from module.params")
    headers = {'Content-Type': 'application/json'}
    data = '{\"originX\": 2.0,\"originY\": 3.0,\"templateId\": \"' + template_id + "\"" + '}'
    resp = requests.post(nifi_url + 'process-groups/' + parent_id + '/template-instance', headers=headers, data=data)
    if (resp.status_code != 201):
        module.fail_json(msg="upload failed status_code=%s" % str(resp.status_code))
#
# upload template
def upload_template(module):
    template_name = module.params['template_name']
    if not template_name:
        module.fail_json(msg="upload: unable to get template_name from module.params")
    template_file = module.params['template_file']
    if not template_file:
         module.fail_json(msg="upload: unable to get template_file from module.params")
    parent_id = module.params['parent_id']
    if not parent_id:
        module.fail_json(msg="upload: unable to get parent_id from module.params")
    nifi_url = module.params['nifi_url']
    if not nifi_url:
        module.fail_json(msg="upload: unable to get nifi_url from module.params")
    url = nifi_url + 'process-groups/' + parent_id + '/templates/upload'
    try:
        files = {'template': (template_name, open(template_file, 'rb')), }
    except IOError as e:
        module.fail_json(msg="upload IOError in %s: %s" % (template_file, str(e)))
    resp = requests.post(url, files=files)
    if (resp.status_code != 201):
        module.fail_json(msg="upload failed status_code=%s" % str(resp.status_code))

#
# get root id for NiFi template
#
def get_parent_id(module):
    nifi_url = module.params['nifi_url']
    resp = requests.get(nifi_url + 'resources')
    lst = resp.json()['resources']
    for d in lst:
        name = d['name']
        if (name == 'NiFi Flow'):
            id = d['identifier']
            if (len(id) > 15 and id[0:16] == '/process-groups/'):
                module.params['parent_id'] = id[16:len(id)]


#
#
def get_id(entity_type, module):
    nifi_url = module.params['nifi_url']
    if not nifi_url:
        module.fail_json(msg="get_id: unable to get nifi_url from module.params")
    entity_name = module.params['template_name']
    if not entity_name:
        module.fail_json(msg="get_id: unable to get template_name from module.params")
    entity_type = '/' + entity_type + '/'
    resp = requests.get(nifi_url + 'resources')
    lst = resp.json()['resources']
    for d in lst:
        name = d['name']
        if (name == entity_name):
            id = d['identifier']
            l = len(entity_type)
            if (len(id) > l and id[0:l] == entity_type):
                module.params['template_id'] = id[l:len(id)]
             
#
def rm_existing_template(module):
    nifi_url = module.params['nifi_url']
    if not nifi_url:
        module.fail_json(msg="rm_existing_template: unable to get nifi_url from module.params")
    entity_name = module.params['template_name']
    if not entity_name:
        module.fail_json(msg="rm_existing_template: unable to get template_name from module.params")
    entity_type = '/templates/'
    resp = requests.get(nifi_url + 'resources')
    lst = resp.json()['resources']
    for d in lst:
        name = d['name']
        if (name == entity_name):
            id = d['identifier']
            l = len(entity_type)
            if (len(id) > l and id[0:l] == entity_type):
                existing_id = id[l:len(id)]
		url = nifi_url + "templates/" + existing_id
		requests.delete(url)
#
# run_module
#
def run_module(module):
    get_template_name(module)
    get_parent_id(module)
    rm_existing_template(module)
    upload_template(module)
    time.sleep(1)
    get_id('templates', module)
    instantiate_template(module)
    return 'ok'

def main():
    fields = {
        "template_file": {"required": True, "type": "str"},
        "nifi_url": {"required": True, "type": "str"},
        "name": {"required": True, "type": "str"},
        "description": {"required": False, "type": "str"},
    }
    module = AnsibleModule(argument_spec=fields)
    result = run_module(module)
    module.exit_json(msg=result)
    #response = {"hello": "world"}
    #module.exit_json(changed=False, meta=response)

if __name__ == '__main__':
    main()
