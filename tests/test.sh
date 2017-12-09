#!/bin/bash

# get domains list
python selectel_dns.py domains_get.json

# add and delete domain
python selectel_dns.py domain_add.json
python selectel_dns.py domain_delete.json

# add domain and record, then add another record, then remove first record, then remove second
python selectel_dns.py domain_add.json
python selectel_dns.py record_add_solo.json
python selectel_dns.py record_add.json
python selectel_dns.py record_add_solo.json
python selectel_dns.py record_delete.json
