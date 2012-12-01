#!/usr/bin/env python
import argparse

import pyes

from wtf.config import Config


def main():
    parser = argparse.ArgumentParser(description='Funkload Server')
    parser.add_argument('--config', help='config file', default='wtf/wtf.ini')
    args = parser.parse_args()

    # loading the config file
    config = Config()
    config.read([args.config])
    settings = config.get_map('wtf')

    # Elastic Search connection
    connection_string = '%(host)s:%(port)s' % {
        'host': settings['elasticsearch.host'],
        'port': settings['elasticsearch.port'],
    }
    es = pyes.ES(connection_string)

    es.delete_index('users')
    es.delete_index('plants')
    es.delete_index('snaps')


if __name__ == '__main__':
    main()
