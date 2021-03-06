import click
import sys
import time

from solar.core import signals
from solar.core.resource import virtual_resource as vr
from solar.dblayer.model import ModelMeta


def run():
    ModelMeta.remove_all()

    resources = vr.create('nodes', 'templates/nodes.yaml', {'count': 2})

    node1, node2 = [x for x in resources if x.name.startswith('node')]
    hosts1, hosts2 = [x for x in resources
                      if x.name.startswith('hosts_file')]

    node1.connect(hosts1, {
        'name': 'hosts:name',
        'ip': 'hosts:ip',
    })

    node2.connect(hosts1, {
        'name': 'hosts:name',
        'ip': 'hosts:ip',
    })

    node1.connect(hosts2, {
        'name': 'hosts:name',
        'ip': 'hosts:ip',
    })

    node2.connect(hosts2, {
        'name': 'hosts:name',
        'ip': 'hosts:ip',
    })

run()
