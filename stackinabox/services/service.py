"""
Stack-In-A-Box: Service Interface
"""
import logging
import re
import uuid

import six


logger = logging.getLogger(__name__)


class RouteAlreadyRegisteredError(Exception):
    pass


class StackInABoxService(object):
    DELETE = 'DELETE'
    GET = 'GET'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'
    METHODS = [
        DELETE,
        GET,
        HEAD,
        OPTIONS,
        PATCH,
        POST,
        PUT
    ]

    def __init__(self, name):
        self.__base_url = '/{0}'.format(name)
        self.__id = uuid.uuid4()
        self.name = name
        self.routes = {
        }
        logger.debug('StackInABoxService ({0}): Hosting Service {1}'
                     .format(self.__id, self.name))

    @staticmethod
    def __get_service_regex(base_url, service_url):
        regex = '^{0}{1}$'.format('', service_url)
        logger.debug('StackInABoxService: {0} + {1} -> {2}'
                     .format(base_url, service_url, regex))
        return re.compile(regex)

    @staticmethod
    def __get_service_url(url, base_url):
        return url[len(base_url):]

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
        logger.debug('StackInABoxService ({0}:{1}) Updating Base URL '
                     'from {2} to {3}'
                     .format(self.__id,
                             self.name,
                             self.__base_url,
                             value))
        self.__base_url = value
        for k, v in six.iteritems(self.routes):
            v['regex'] = StackInABoxService.__get_service_regex(value,
                                                                v['uri'])

    def reset(self):
        logger.debug('StackInABoxService ({0}): Reset'
                     .format(self.__id, self.name))
        self.base_url = '/{0}'.format(self.name)
        logger.debug('StackInABoxService ({0}): Hosting Service {1}'
                     .format(self.__id, self.name))

    def request(self, method, request, uri, headers):
        logger.debug('StackInABoxService ({0}:{1}): Received {2} - {3}'
                     .format(self.__id, self.name, method, uri))
        uri_path = uri
        if '?' in uri:
            logger.debug('StackInABoxService ({0}:{1}): Found query string '
                         'removing for match operation.'
                         .format(self.__id, self.name))
            uri_path, uri_qs = uri.split('?')
            logger.debug('StackInABoxService ({0}:{1}): uri =  "{2}", '
                         'query = "{3}"'
                         .format(self.__id, self.name, uri_path, uri_qs))

        for k, v in six.iteritems(self.routes):
            logger.debug('StackInABoxService ({0}:{1}): Checking if '
                         'route {2} handles...'
                         .format(self.__id, self.name, v['uri']))
            logger.debug('StackInABoxService ({0}:{1}): ...using regex '
                         'pattern {2} against {3}'
                         .format(self.__id,
                                 self.name,
                                 v['regex'].pattern,
                                 uri_path))
            if v['regex'].match(uri_path):
                logger.debug('StackInABoxService ({0}:{1}): Checking if '
                             'route {2} handles method {2}...'
                             .format(self.__id, self.name, v['uri'], method))
                if method in v['handlers']:
                    logger.debug('StackInABoxService ({0}:{1}): Calling '
                                 'handler for route {2} on method {3}...'
                                 .format(self.__id,
                                         self.name,
                                         v['uri'],
                                         method))
                    return v['handlers'][method](self,
                                                 request,
                                                 uri,
                                                 headers)
        return (500, headers, 'Server Error')

    def register(self, method, uri, call_back):
        found = False

        if uri not in self.routes.keys():
            logger.debug('Service ({0}): Creating routes'
                         .format(self.name))
            self.routes[uri] = {
                'regex': StackInABoxService.__get_service_regex(self.base_url,
                                                                uri),
                'uri': uri,
                'handlers': {
                }
            }

        if method not in self.routes[uri]['handlers'].keys():
            logger.debug('Service ({0}): Adding route for {1}'
                         .format(self.name, method))
            self.routes[uri]['handlers'][method] = call_back
        else:
            RouteAlreadyRegisteredError(
                'Service ({0}): Route {1} already registered'
                .format(self.name, uri))
