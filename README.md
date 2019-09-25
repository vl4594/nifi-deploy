nifi-deploy -- ansible module for deployment of Apache NiFi Processor Group templates
======================================================================
## DESCRIPTION
This module automates process of deployment and instantiation for Apache Nifi Pocessor Group templates
## REQUIRED
Apache NiFi (1.7.0), Ansible (2.8.4), Python (2.7.6)
## CLI
ansible-playbook play.yml

## REQUIRED ARGUMENTS
template file (xml)
NiFi server url

## PLAYBOOK EXAMPLE
- name: deploy template
  hosts: localhost
  tasks:
  - name: run the new module
    nifi-deploy:
      nifi_url: 'http://localhost:8080/nifi-api/'
      template_file: 'test_template.xml' 
      name: 'deploy'




