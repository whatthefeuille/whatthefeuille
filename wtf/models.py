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
    connection = pyes.ES(connection_string)
    settings['elasticsearch'] = connection

    # Create indexes and mappings
    create_indexes(connection)


USER_MAPPING = {
    'id': {
        'type': 'string',
        'store': 'yes',
        'index': 'not_analyzed',
    },
    'email': {
        'type': 'string',
        'store': 'yes',
        'index': 'not_analyzed',
    },
    'registered': {
        'type': 'date',
        'store': 'yes',
    },
}


PLANT_MAPPING = {
    'id': {
        'type': 'string',
        'store': 'yes',
        'index': 'not_analyzed',
    },
    'name': {
        'type': 'string',
        'store': 'yes',
    },
    'common_name': {
        'type': 'string',
        'store': 'yes',
    },
    'abstract': {
        'type': 'string',
        'store': 'yes',
    },
    'picture': {
        'type': 'string',
        'store': 'yes',
        'index': 'not_analyzed',
    },
    'dbpedia': {
        'type': 'string',
        'store': 'yes',
        'index': 'not_analyzed',
    },
}


SNAP_MAPPING = {
    'user': {
        'type': 'string',
    },
    'timestamp': {
        'type': 'date',
        'store': 'yes',
    },
    'description': {
        'type': 'string',
        'store': 'yes',
    },
    'location': {
        'type': 'geo_point',
        'lat_lon': 'true',
    },
    'filename': {
        'type': 'string',
        'store': 'yes',
        'index': 'not_analyzed',
    },
    'base_x': {
        'type': 'integer',
        'store': 'yes',
    },
    'base_y': {
        'type': 'integer',
        'store': 'yes',
    },
    'top_x': {
        'type': 'integer',
        'store': 'yes',
    },
    'top_y': {
        'type': 'integer',
        'store': 'yes',
    },
    'plant': {
        'type': 'string',
        'store': 'yes',
    },
    'likes': {
        'type': 'integer',
        'store': 'yes',
    },
}


def create_indexes(es):

    es.create_index_if_missing('users')
    es.put_mapping('usertype', {'properties': USER_MAPPING}, ['users'])

    es.create_index_if_missing('plants')
    es.put_mapping('planttype', {'properties': PLANT_MAPPING}, ['plants'])

    es.create_index_if_missing('snaps')
    es.put_mapping('snaptype', {'properties': SNAP_MAPPING}, ['snaps'])
