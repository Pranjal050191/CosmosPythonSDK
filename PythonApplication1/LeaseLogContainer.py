from gc import enable
import os
import datetime
from pydoc import Doc
from azure.cosmos import CosmosClient, ThroughputProperties, database, exceptions
from azure.cosmos.partition_key import PartitionKey

# Cosmos DB connection details
endpoint = "https://cosmosdbact1018.documents.azure.com:443/"
key = "OQY7aYAH1hjjfOpWl6DJUlMzH2QtHPWvq4QuP0W5UByYfpWxcTcNfCxwFQfG90OIS36EPCQze7CtACDbAdm5ag=="

# Initialize the Cosmos client
# This also automatically handles the bulk mode
client = CosmosClient(endpoint, key)

try:
    # Creating database
    print("Executing new file")
   
    database_name = "cosmosworks"
    database = client.create_database_if_not_exists(id=database_name)

    # to get existing database
    #database = client.get_database_client("cosmosworks")
    print("New Database ID: ", database.id)

    # Define custom indexing policy
    indexing_policy = {
    "indexingMode": "consistent",  # Options: 'consistent', 'lazy', or 'none'
    "automatic": True,  # Enables automatic indexing
    "includedPaths": [
        {"path": "/*"}
        ,{"path": "/productName/?", "indexes": [{"kind": "Range", "dataType": "String"}]}
        ,{"path": "/price/?", "indexes": [{"kind": "Range", "dataType": "Number"}]}
    ],
    "excludedPaths": [
        {"path": "/\"_etag\"/?"}  # Excludes 'etag' from indexing
    ]
}

    #Creating Container with autoscale
    container_lease = database.create_container_if_not_exists(
        id="productslease"
       ,partition_key=PartitionKey(path="/partitionKey")
       ,offer_throughput=400 #This sets autoscale throughput (autoscaling between 40 - 400 RU/s)
    )

    print("New container container_lease :",container_lease.id)

    container = database.create_container_if_not_exists(
        id="products"
       ,partition_key=PartitionKey(path="/categoryId")
       ,indexing_policy=indexing_policy
       ,offer_throughput=600 #This sets autoscale throughput (autoscaling between 60 - 600 RU/s)
    )

    #We can get container if it already exists
    #container = database.get_container_client("products")

    print("New container :",container.id)

    #Update container to enable autoscale
    print(f"Container '{container.id}' updated with autoscale throughput enabled")

    # Function to log changes to the productslease container
    def log_change(operation, document):
        # Generate a unique ID for each log entry using the document ID and timestamp
        unique_log_id = f"{document['id']}_{datetime.datetime.utcnow().isoformat()}"

        log_entry = {
            "id": unique_log_id,  # Unique ID to avoid overwriting
            "operation": operation,  # Type of operation (CREATE, UPDATE, DELETE)
            "timestamp": datetime.datetime.utcnow().isoformat(),  # Timestamp of the operation
            "productName": document.get("productName", ""),
            "categoryId": document.get("categoryId", ""),
            "price": document.get("price", ""),
        }
        # Insert log entry into productslease
        container_lease.upsert_item(body=log_entry)
        print(f"Logged {operation} operation for document ID {document['id']} in productslease.")

    # Example CRUD operations
    def create_product(document):
        container.create_item(body=document)
        log_change("CREATE", document)

    def update_product(document):
        container.replace_item(item=document["id"], body=document)
        log_change("UPDATE", document)

    def delete_product(document_id, partition_key):
        try:
            # Fetch the document before deletion
            document = container.read_item(item=document_id, partition_key=partition_key)
        
            # Log the DELETE operation with the full document details
            log_change("DELETE", document)
        
            # Perform the actual deletion
            container.delete_item(item=document_id, partition_key=partition_key)
            print(f"Deleted document with ID {document_id}.")

        except exceptions.CosmosResourceNotFoundError:
            print(f"Document with ID {document_id} not found.")
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
        

    # Example usage
    new_product = {
        "id": "5",
        "productName": "Tablet",
        "categoryId": "Electronics",
        "price": 250
    }

    # Create a new product and log the operation
    create_product(new_product)

    # Updating a product and logging the operation
    updated_product = {
        "id": "5",
        "productName": "High-End Tablet",
        "categoryId": "Electronics",
        "price": 350
    }
    update_product(updated_product)

    # Deleting a product and logging the operation
    delete_product("5", "Electronics")

except exceptions.CosmosHttpResponseError as e:
    print(f"Cosmos DB Error: {e.message}")
except exceptions.CosmosResourceNotFoundError:
    print(f"Document with ID {document_id} not found.")
except Exception as e:
    print(f"General Error: {str(e)}")


#First commit
