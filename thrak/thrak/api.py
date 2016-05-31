#!/usr/bin/env python
# encoding: utf-8
import os
from flask import Flask
import flask_restful as restful
from flask_restful import reqparse
from models import Service, ServiceDoesNotExist

DEBUG = True if os.getenv('DEBUG') and os.getenv('DEBUG').lower() == 'true' else False

app = Flask(__name__)
api = restful.Api(app)
parser = reqparse.RequestParser()
parser.add_argument('name', type=str)


def get_service_or_404(host, port):
    try:
        service = Service.get(host, port)
    except ServiceDoesNotExist:
        restful.abort(404, message="Service {}:{} doesn't exist".format(host, port))
    return service


class ServiceResource(restful.Resource):
    def get(self, host, port):
        return get_service_or_404(host, port).data

    def delete(self, host, port):
        service = get_service_or_404(host, port)
        service.delete(host, port)
        # TODO better to use 202 with async
        return '', 204

    # TODO
    def put(self, service_id):
        restful.abort(404, message="API not finish yet")
        args = parser.parse_args()
        service = {'name': args['name']}
        Service.create(service_id, service)
        return service.data, 201


class ServiceListResource(restful.Resource):
    def get(self, host):
        return list(s.data for s in Service.get_by_host(host))

    # TODO
    def post(self):
        restful.abort(404, message="API not finish yet")
        args = parser.parse_args()
        service_id = int(max(SERVICES.keys()).lstrip('service_id_')) + 1
        service_id = 'service_id_%i' % service_id
        SERVICES[service_id] = {'task': args['task']}
        return SERVICES[service_id], 201


if __name__ == '__main__':
    api.add_resource(ServiceListResource, '/services/<host>')
    api.add_resource(ServiceResource, '/services/<host>/<port>')
    app.run(host='0.0.0.0', debug=DEBUG)
