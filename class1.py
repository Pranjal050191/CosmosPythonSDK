from gc import enable
import os
from pydoc import Doc
from azure.cosmos import CosmosClient, ThroughputProperties, database, exceptions
from azure.cosmos.partition_key import PartitionKey

# Cosmos DB connection details
endpoint = "https://cosmosdbact1018.documents.azure.com:443/"
key = "OQY7aYAH1hjjfOpWl6DJUlMzH2QtHPWvq4QuP0W5UByYfpWxcTcNfCxwFQfG90OIS36EPCQze7CtACDbAdm5ag=="

# Initialize the Cosmos client
# This also automatically handles the bulk mode
client = CosmosClient(endpoint, key)
database = client.create_database_if_not_exists("cosmosworks")
print("New Database ID: ", database.id)

# Define custom indexing policy
indexing_policy = {
    "indexingMode": "consistent",  # Options: 'consistent', 'lazy', or 'none'
    "automatic": True,  # Enables automatic indexing
    "includedPaths": [
        {"path": "/productName/?", "indexes": [{"kind": "Range", "dataType": "String"}]},
        {"path": "/price/?", "indexes": [{"kind": "Range", "dataType": "Number"}]},
    ],
    "excludedPaths": [
        {"path": "/etag/?"}  # Excludes 'etag' from indexing
    ]
}

#Creating Container with autoscale
container = database.create_container_if_not_exists(
   id="products"
  ,partition_key=PartitionKey(path="/categoryId")
  ,indexing_policy=indexing_policy
  ,offer_throughput=1000 #This sets autoscale throughput (autoscaling between 100 - 1000 RU/s)
 )

print("New container :",container.id)