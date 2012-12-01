import pyes


import logging
log = logging.getLogger(__name__)


def includeme(config):

    settings = config.registry.settings

    # Elastic Search connection
    connection_string = '%(host)s:%(port)s' % {
        'host': settings['elasticsearch.host'],
        'port': settings['elasticsearch.port'],
    }
    log.info("Connecting to Elastic Search on %s", connection_string)
    settings['elasticsearch'] = pyes.ES(connection_string)
