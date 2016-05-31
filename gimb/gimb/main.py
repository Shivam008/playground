# encoding: utf-8
import time
from nazg import get_docker_client, EtcdConf, PUBLIC_HOST

DEFAULT_REFRESH_FREQUENCY = 5


class GimbAgent(object):

    def __init__(self, frequency=DEFAULT_REFRESH_FREQUENCY):
        self.docker = get_docker_client()
        self.etcd = EtcdConf()
        self.frequency = frequency

    @property
    def containers(self):
        return self.docker.containers()

    @property
    def service_ttl(self):
        return self.frequency * 2

    def do_registrations(self):
        for container in self.containers:
            self._register(container)

    def _register(self, container):
        image = container['Image']
        container_id = container['Id']
        container_name = ' '.join(container['Names'])
        for mapping in container['Ports']:
            public_port = mapping.get('PublicPort')
            if public_port is not None:
                self._register_port(public_port, container_id,
                                    container_name, image)

    def _register_port(self, public_port, container_id, container_name, image):
        print 'will create_service({}, {}, {}, {}, {})'.format(
            self.service_ttl,
            public_port,
            container_id,
            container_name,
            image,
        )
        service = self.etcd.create_service(self.service_ttl, public_port,
                                           container_id=container_id,
                                           container_name=container_name,
                                           image=image)
        print 'created service:', service

    def run_forever(self):
        while True:
            start_time = time.time()
            self.do_registrations()
            end_time = time.time()

            diff = start_time + self.frequency - end_time
            if diff > 0:
                time.sleep(diff)
            else:
                # should log error
                print 'Too long in a loop, will double the frequency'
                self.frequency *= 2

            print '\nAll services:'
            print list(self.etcd.iter_host_services(PUBLIC_HOST)), '\n'


def main():
    agent = GimbAgent()
    agent.run_forever()


if __name__ == '__main__':
    main()
