from google.cloud.sql.connector import Connector
from google.cloud import secretmanager
import sqlalchemy

def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")
    return payload


connector = Connector()

password = access_secret_version('c241-ps193', 'mysql_password', '1')

def getconn():
    conn = connector.connect(
        "c241-ps193:asia-southeast2:c241-ps193-db",
        "pymysql",
        user="root",
        password=password,
        db="db_herba_guide",
    )
    return conn

def create_connection_pool():
    return sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        pool_size=5,
        max_overflow=10  
    )
