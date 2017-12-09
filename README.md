# Ansible Selectel DNS API module

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

Inspired by [dnsimple module](http://docs.ansible.com/ansible/latest/dnsimple_module.html)
