import pymongo
from kubernetes import client
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from src.components.config import APIServerConfig


def get_k8s_client(opt: APIServerConfig, debug: bool = False) -> client:
    """
    Get Kubernetes client.
    """

    api_server = f"https://{opt.k8s_host}:{str(opt.k8s_port)}"
    ca_cert_path = opt.k8s_ca_cert
    token_path = opt.k8s_token
    with open(token_path, "r") as f:
        token = f.read()

    # Set the configuration
    configuration = client.Configuration()
    configuration.ssl_ca_cert = ca_cert_path
    configuration.host = api_server
    configuration.verify_ssl = opt.k8s_verify_ssl
    configuration.debug = debug
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)

    return client


def get_db_uri(opt: APIServerConfig) -> str:
    """
    Get MongoDB URI
    """
    return 'mongodb://{account}{host}:{port}'.format(
        account='{username}:{password}@'.format(
            username=opt.db_username,
            password=opt.db_password) if opt.db_username else '',
        host=opt.db_host if opt.db_host else '127.0.0.1',
        port=opt.db_port if opt.db_port else 27017)


def get_mongo_db_connection(opt: APIServerConfig) -> pymongo.MongoClient:
    """
    Get MongoDB connection
    """
    _db_uri = get_db_uri(opt)
    logger.debug(f"connecting to MongoDB at {_db_uri}")
    conn = pymongo.MongoClient(_db_uri, connect=True)
    return conn


def get_async_mongo_db_connection(opt: APIServerConfig) -> AsyncIOMotorClient:
    """
    Get MongoDB connection Async
    """
    _db_uri = get_db_uri(opt)
    logger.debug(f"connecting to MongoDB at {_db_uri}")
    return AsyncIOMotorClient(_db_uri)
