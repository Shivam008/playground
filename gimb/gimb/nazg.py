# encoding: utf-8
import os
import json
import etcd as etcd_api
import docker as docker_api

PUBLIC_HOST = os.environ.get('PUBLIC_HOST')
ETCD_HOST = os.environ.get('ETCD_HOST', '127.0.0.1')
ETCD_PORT = os.environ.get('ETCD_PORT', 4001)
ETCD_SERVICES_PATH = os.environ.get('ETCD_SERVICES_PATH',
                                    '/services').rstrip('/')
DOCKER_BASE_URL = os.environ.get('DOCKER_BASE_URL',
                                 'unix://var/run/docker.sock')
DOCKER_CONNECT_TIMEOUT = os.environ.get('DOCKER_CONNECT_TIMEOUT', 300)


def get_docker_client(base_url=None):
    return docker_api.Client(
        base_url=base_url or DOCKER_BASE_URL,
        timeout=DOCKER_CONNECT_TIMEOUT,
    )


class EtcdConf(object):
    '''\
services/
    <host>/
        <port>/
            id
            name
    '''

    def __init__(self):
        self.client = etcd_api.Client(host=ETCD_HOST, port=ETCD_PORT)

    def _write(self, **entry):
        return self.client.write(
            entry['key'].encode('utf-8'),
            entry['value'].encode('utf-8'),
            ttl=entry['ttl']
        )

    @staticmethod
    def _serialize_entry(self, entry):
        return {
            'key': entry.key,
            'value': entry.value,
            'ttl': entry.ttl,
            'dir': entry.dir,
        }

    def get_service(self, host, port):
        service_key = '{services_path}/{host}/{port}'.format(
            services_path=ETCD_SERVICES_PATH,
            host=host,
            port=port,
        )
        return self.loads_service_attributes(service_key)

    def iter_host_services(self, host):
        host_key = '{services_path}/{host}'.format(
            services_path=ETCD_SERVICES_PATH,
            host=host,
        )

        try:
            services = self.client.read(host_key)
        # stop iterator while no /sevices directory
        except etcd_api.EtcdKeyNotFound:
            raise StopIteration

        # stop iterator while no sevices
        if services.value is None:
            raise StopIteration

        for service in services.leaves:
            yield self.loads_service_attributes(service.key)

    def create_service(self, ttl, port, host=PUBLIC_HOST, **extra):
        service_key = '{services_path}/{host}/{port}'.format(
            services_path=ETCD_SERVICES_PATH,
            host=host,
            port=port,
        )
        self._write(key=service_key, value=json.dumps(extra), ttl=ttl)
        return self.loads_service_attributes(service_key)

    def loads_service_attributes(self, service_key):
        try:
            service = self.client.read(service_key)
        except etcd_api.EtcdKeyNotFound:
            return None
        data = json.loads(service.value)
        data['host'], data['public_port'] = service_key.rsplit('/', 2)[-2:]
        return data


class Container(object):
    def __init__(self, container_id, client=None):
        self._docker = client or get_docker_client()
        self.id = container_id
        self.inspect_info = self.get_inspect_info()
        self.name = self.inspect_info['Name']
        self.image_name = self.inspect_info['Config']['Image']

    @classmethod
    def get(cls, container_id, docker_base_url=None):
        base_url = docker_base_url or DOCKER_BASE_URL
        return cls(container_id, get_docker_client(base_url))

    @classmethod
    def create(cls, docker_base_url=None, **kwargs):
        base_url = docker_base_url or DOCKER_BASE_URL
        client = get_docker_client(base_url)
        host_config = client.create_host_config(port_bindings={
            int(port): None for port in kwargs.get('ports', [])})
        container = client.create_container(host_config=host_config, **kwargs)
        client.start(container.get('Id'))
        return cls(container.get('Id'), client)

    def get_inspect_info(self):
        return self._docker.inspect_container(self.id)

    def iter_service_ports(self):
        for port_setting in self.inspect_info['NetworkSettings']['Ports'].values():
            for mapping in port_setting:
                public_port = mapping.get('HostPort')
                if public_port is not None:
                    yield int(public_port)

    def delete(self):
        self._docker.stop(self.id)
        return self._docker.remove_container(self.id)
