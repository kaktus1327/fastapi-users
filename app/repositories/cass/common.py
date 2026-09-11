import os

from cassandra.cluster import Cluster
from dotenv import load_dotenv


def get_cluster_session():
    load_dotenv()
    contact_points = os.getenv("CASSANDRA_CONTACT_POINTS", "").split(",")
    port = int(os.getenv("CASSANDRA_PORT", 9042))
    keyspace = os.getenv("CASSANDRA_KEYSPACE")

    cluster = Cluster(contact_points=contact_points, port=port)
    session = cluster.connect(keyspace)
    return cluster, session
