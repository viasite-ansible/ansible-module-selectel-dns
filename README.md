# selectel_dns, Ansible Selectel DNS API module

# Installation
1. Install selectel-dns-api:
```
pip install selectel-dns-api
```
2. Copy selectel_dns.py to your modules directory
3. Add modules directory to ansible.cfg (`library = path/to/modules`)

# Test
Replace ansible-selectel-dns.ru to your domain.

``` bash
bash test.sh
```

Inspired by [dnsimple module](http://docs.ansible.com/ansible/latest/dnsimple_module.html).

Documentation generated with [jedelman8/ansible-webdocs](https://github.com/jedelman8/ansible-webdocs).

### *Manage DNS domains and records on Selectel DNS hosting*

---
### Requirements
* selecte-dns-api

---
### Modules

  * [selectel_dns - interface with selectel dns hosting.](#selectel_dns)

---

## selectel_dns
Interface with Selectel DNS hosting.

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Manages domains and records via the Selectel DNS API, see the docs: U(https://my.selectel.ru/domains/doc)

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| solo  |   no  |  | |  Whether the record should be the only one for that record type and record name. Only use with state=present on a record  |
| domain  |   no  |  | |  Domain to work with. Can be the domain name (e.g. "mydomain.com") or the numeric ID of the domain in Selectel. If omitted, a list of domains will be returned.  If domain is present but the domain doesn't exist, it will be created.  |
| ttl  |   no  |  3600 (one hour)  | |  The TTL to give the new record  |
| value  |   no  |  | |  Record value  Must be specified when trying to ensure a record exists  |
| priority  |   no  |  | |  Record priority  |
| record  |   no  |  | |  Record to add, if blank a record for the domain will be created, supports the wildcard (*)  |
| state  |   no  |  | <ul> <li>present</li>  <li>absent</li> </ul> |  whether the record should exist or not  |
| api_token  |   no  |  | |  Account API token. If omitted, the env variable SELECTEL_API_TOKEN will be looked for.  |
| type  |   no  |  | <ul> <li>A</li>  <li>CNAME</li>  <li>MX</li>  <li>SPF</li>  <li>TXT</li>  <li>NS</li>  <li>SRV</li>  <li>AAAA</li> </ul> |  The type of DNS record to create  |


 
#### Examples

``` yaml

# create domain
- selectel_dns:
    domain: my.com
    state: present
  delegate_to: localhost

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

```
