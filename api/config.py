import os

# AWS DocumentDB Connection URI (Ensure you replace with your actual password or use an environment variable)
MONGO_URI = "mongodb://replicator:<insertYourPassword>@replication-service-db.cluster-c9e68ewiku3r.eu-central-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

# Database and Collection Configurations
DB_NAME = "replicationDB"  # Change this to your actual DocumentDB database name
CACHE_COLLECTION = "cacheState"
DOCUMENT_ID = "LRUCache"

# Securely store the password using an environment variable
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "<insertYourPassword>")

# Replace the placeholder password in the URI if the environment variable is set
if MONGO_PASSWORD != "<insertYourPassword>":  # Prevents accidental hardcoded passwords
    MONGO_URI = MONGO_URI.replace("<insertYourPassword>", MONGO_PASSWORD)

# Define the base directory where the script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the AWS TLS certificate (Ensure this file exists in the `src/` directory)
TLS_CA_FILE = os.path.join(BASE_DIR, "global-bundle.pem")

# Ensure the TLS certificate file exists before connecting
if not os.path.exists(TLS_CA_FILE):
    raise FileNotFoundError(f"TLS certificate file not found: {TLS_CA_FILE}. "
                            "Download it using: curl -o global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem")
