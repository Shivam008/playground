#!/usr/bin/env python
# encoding: utf-8
import os
import time
from nazg import EtcdConf, Container

DOCKER_BASE_URL = 'tcp://{host}:%s' % os.getenv('DOCKER_PORT', 2375)
etcd = EtcdConf()


class ServiceDoesNotExist(Exception):
    pass


class Service(object):

    def __init__(self, data):
        self.data = data

    @property
    def container_id(self):
        return self.data['container_id']

    @classmethod
    def get(cls, host, port):
        service = etcd.get_service(host, port)
        if service is None:
            raise ServiceDoesNotExist('lost Service(%s:%s) in etcd' % (host, port))
        return cls(service)

    @classmethod
    def get_by_host(cls, host):
        services = etcd.iter_host_services(host)
        for service in services:
            if service is not None:
                yield cls(service)

    @classmethod
    def create(cls, host, **kwargs):
        docker_base_url = DOCKER_BASE_URL.format(host=host)
        container = Container.create(docker_base_url, **kwargs)

        services = []
        for public_port in container.iter_service_ports():
            while True:
                try:
                    services.append(cls.get(host, public_port))
                    break
                except ServiceDoesNotExist:
                    time.sleep(1)

        return services

    def delete(self, host, port):
        container_id = self.get(host, port).container_id
        docker_base_url = DOCKER_BASE_URL.format(host=host)
        return Container.get(container_id, docker_base_url).delete()
