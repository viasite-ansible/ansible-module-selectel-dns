#!/usr/bin/python

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.0'}

DOCUMENTATION = '''
---
module: selectel_dns
short_description: Interface with Selectel DNS hosting.
description:
   - "Manages domains and records via the Selectel DNS API, see the docs: U(https://my.selectel.ru/domains/doc)"
options:
  api_token:
    description:
      - Account API token. If omitted, the env variable SELECTEL_API_TOKEN will be looked for.
    required: false
    default: null

  domain:
    description:
      - Domain to work with. Can be the domain name (e.g. "mydomain.com") or the numeric ID of the domain in Selectel. If omitted, a list of domains will be returned.
      - If domain is present but the domain doesn't exist, it will be created.
    required: false
    default: null

  record:
    description:
      - Record to add, if blank a record for the domain will be created, supports the wildcard (*)
    required: false
    default: null

  type:
    description:
      - The type of DNS record to create
    required: false
    choices: [ 'A', 'CNAME', 'MX', 'SPF', 'TXT', 'NS', 'SRV', 'AAAA' ]
    default: null

  ttl:
    description:
      - The TTL to give the new record
    required: false
    default: 3600 (one hour)

  value:
    description:
      - Record value
      - "Must be specified when trying to ensure a record exists"
    required: false
    default: null

  priority:
    description:
      - Record priority
    required: false
    default: null

  state:
    description:
      - whether the record should exist or not
    required: false
    choices: [ 'present', 'absent' ]
    default: null

  solo:
    description:
      - Whether the record should be the only one for that record type and record name. Only use with state=present on a record
    required: false
    default: null

requirements: [ selectel_dns_api ]
author: "Stanislav Popov (@popstas)"
'''

EXAMPLES = '''
# authenticate using API token and fetch all domains
- selectel_dns:
    account_api_token: dummyapitoken
  delegate_to: localhost

# fetch my.com domain records
- selectel_dns:
    domain: my.com
    state: present
  delegate_to: localhost
  register: records

# delete a domain
- selectel_dns:
    domain: my.com
    state: absent
  delegate_to: localhost

# create a test.my.com A record to point to 127.0.0.01
- selectel_dns:
    domain: my.com
    record: test
    type: A
    value: 127.0.0.1
  delegate_to: localhost
  register: record

# create a my.com CNAME record to example.com
- selectel_dns
    domain: my.com
    record: ''
    type: CNAME
    value: example.com
    state: present
  delegate_to: localhost

# change it's ttl
- selectel_dns:
    domain: my.com
    record: ''
    type: CNAME
    value: example.com
    ttl: 600
    state: present
  delegate_to: localhost

# and delete the record
- selectel_dns:
    domain: my.com
    record: ''
    type: CNAME
    value: example.com
    state: absent
  delegate_to: localhost
'''

import os
import re
from ansible.module_utils.basic import AnsibleModule
try:
    import selectel_dns_api
    from selectel_dns_api.rest import ApiException
    HAS_SELECTEL_DNS = True
except ImportError:
    HAS_SELECTEL_DNS = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_token=dict(required=False, no_log=True),
            domain=dict(required=False),
            record=dict(required=False),
            type=dict(required=False, choices=[
                      'A', 'CNAME', 'MX', 'SPF', 'TXT', 'NS', 'SRV', 'AAAA']),
            ttl=dict(required=False, default=3600, type='int'),
            value=dict(required=False),
            priority=dict(required=False, type='int'),
            state=dict(required=False, choices=['present', 'absent']),
            solo=dict(required=False, type='bool'),
        ),
        required_together=(
            ['record', 'value']
        ),
        supports_check_mode=True,
    )

    if not HAS_SELECTEL_DNS:
        module.fail_json(msg="selectel-dns-api required for this module")

    api_token = module.params.get('api_token')
    domain = module.params.get('domain')
    record = module.params.get('record')
    record_type = module.params.get('type')
    ttl = module.params.get('ttl')
    value = module.params.get('value')
    priority = module.params.get('priority')
    state = module.params.get('state')
    is_solo = module.params.get('solo')

    if not api_token and os.environ.get('SELECTEL_API_KEY'):
        api_token = os.environ.get('SELECTEL_API_KEY')
    else:
        module.fail_json(
            msg="You must define api_token or env SELECTEL_API_KEY")

    config = selectel_dns_api.rest.Configuration()
    config.api_key = {'X-Token': api_token}
    domains_api = selectel_dns_api.DomainsApi()
    records_api = selectel_dns_api.RecordsApi()

    try:
        # No domain, return a list
        if not domain:
            domains = domains_api.get_domains()
            module.exit_json(changed=False, result=[d.name for d in domains])

        # Domain & No record
        if domain and record is None:
            domains = domains_api.get_domains()
            dr = next((d for d in domains if d.name == domain), None)
            if state == 'present':
                if dr:
                    module.exit_json(changed=False, result=dr.to_dict())
                else:
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        data = selectel_dns_api.NewDomain(domain)
                        module.exit_json(
                            changed=True, result=domains_api.add_domain(data).name)
            elif state == 'absent':
                if dr:
                    if not module.check_mode:
                        domains_api.delete_domain(dr.id)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)
            else:
                module.fail_json(
                    msg="'%s' is an unknown value for the state argument" % state)

        # need the not none check since record could be an empty string
        if domain and record is not None:
            try:
                dr = domains_api.get_domain_by_name(str(domain))
            except ApiException as e:
                if e.status == 404:
                    module.fail_json(msg="Domain not exists")
                else:
                    module.fail_json(msg="Unable to contact Selectel: %s" % e)

            if not record_type:
                module.fail_json(msg="Missing the record type")

            if not value:
                module.fail_json(msg="Missing the record value")

            if record == '':
                record = dr.name

            if not re.search('%s$' % dr.name, record):
                record = '%s.%s' % (record, dr.name)

            records = records_api.get_resource_records_by_domain_id(dr.id)

            rr = next((r for r in records if r.name == record and r.type
                       == record_type and r.content == value), None)

            if state == 'present':
                changed = False
                if is_solo:
                    # delete any records that have the same name and record type
                    same_type = [r.id for r in records if r.name
                                 == record and r.type == record_type]
                    if rr:
                        same_type = [rid for rid in same_type if rid != rr.id]
                    if same_type:
                        if not module.check_mode:
                            for rid in same_type:
                                records_api.delete_resource_record(dr.id, rid)
                        changed = True
                if rr:
                    # check if we need to update
                    if rr.ttl != ttl or rr.priority != priority:
                        data = selectel_dns_api.NewOrUpdatedRecord(
                            name=record,  type=record_type, content=value)
                        if ttl:
                            data.ttl = ttl
                        if priority:
                            data.priority = priority
                        if module.check_mode:
                            module.exit_json(changed=True)
                        else:
                            rr = records_api.update_resource_record(dr.id, rr.id, data)
                            module.exit_json(changed=True, result=rr.to_dict())
                    else:
                        module.exit_json(changed=changed, result=rr.to_dict())
                else:
                    # create it
                    data = selectel_dns_api.NewOrUpdatedRecord(
                        name=record,  type=record_type, content=value)

                    if ttl:
                        data.ttl = ttl
                    if priority:
                        data.priority = priority
                    if module.check_mode:
                        module.exit_json(changed=True)
                    else:
                        rr = records_api.add_resource_record(data, dr.id)
                        module.exit_json(changed=True, result=rr.to_dict())
            elif state == 'absent':
                if rr:
                    if not module.check_mode:
                        records_api.delete_resource_record(dr.id, rr.id)
                    module.exit_json(changed=True)
                else:
                    module.exit_json(changed=False)
            else:
                module.fail_json(
                    msg="'%s' is an unknown value for the state argument" % state)

    except ApiException as e:
        module.fail_json(msg="Unable to contact Selectel: %s" % e)

    module.fail_json(msg="Unknown what you wanted me to do")


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.pycompat24 import get_exception

if __name__ == '__main__':
    main()
