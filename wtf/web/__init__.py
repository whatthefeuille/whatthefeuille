from pyramid.config import Configurator
from pyramid.decorator import reify
from pyramid.request import Request as BaseRequest

from pyramid_beaker import session_factory_from_settings


class Request(BaseRequest):
    """
    Custom request class
    """

    @reify
    def elasticsearch(self):
        """
        Get the Elastic Search connection
        """
        settings = self.registry.settings
        return settings['elasticsearch']


def main(global_config, **settings):
    # defaults
    if 'mako.directories' not in settings:
        settings['mako.directories'] = 'wtf:templates'

    session_factory = session_factory_from_settings(settings)

    # creating the config
    config = Configurator(settings=settings, session_factory=session_factory)

    config.include('wtf.models')

    # thumbs
    config.include('wsgithumb')
    config.add_thumb_view('thumbs')

    # Use our custom Request class
    config.set_request_factory(Request)

    # routing
    config.add_route('index', '/')
    config.add_route('profile', '/profile')
    config.add_route('sign', '/sign')
    config.add_route('logout', '/logout')
    config.add_route('about_file', '/about/{file:.*}')
    config.add_route('about_index', '/about')

    config.add_static_view('media', 'wtf:media/')

    config.scan("wtf.web.views")
    return config.make_wsgi_app()
