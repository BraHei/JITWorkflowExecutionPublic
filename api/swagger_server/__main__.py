#!/usr/bin/env python3

import connexion
from swagger_server import encoder
from swagger_server.managers.mongodbmanager import MongoDBManager
from swagger_server.managers.cachemanager import CacheManager
from swagger_server.managers.workfloweventhandler import WorkflowEventHandler

cache_manager = CacheManager()

workflow_event_handler = WorkflowEventHandler(cache_manager)

def main():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Replication API'}, pythonic_params=True)
    app.run(port=8080, debug=True)

if __name__ == '__main__':
    main()
