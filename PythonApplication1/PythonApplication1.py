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

try:
    print("Executing old file")
    # Get database account properties
    account_properties = client.get_database_account()
    print("Account Endpoint:", account_properties.DatabasesLink)
    print("Account Properties:")
    for key, value in vars(account_properties).items():
        print(f"{key}: {value}")
    # Extract account endpoint and region
    writable_locations = account_properties._WritableLocations
    readable_locations = account_properties._ReadableLocations

    # Assuming the first writable and readable location is the desired one
    if writable_locations:
        writable_region = writable_locations[0]['name']
        writable_endpoint = writable_locations[0]['databaseAccountEndpoint']
    
    if readable_locations:
        readable_region = readable_locations[0]['name']
        readable_endpoint = readable_locations[0]['databaseAccountEndpoint']
    
    print("Account Writable Region:", writable_region)
    print("Account Writable Endpoint:", writable_endpoint)
    print("Account Readable Region:", readable_region)
    print("Account Readable Endpoint:", readable_endpoint)
    
    # Creating database
    database = client.create_database_if_not_exists(
        id = "cosmosworks"
        )

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

    container = database.create_container_if_not_exists(
        id="products"
       ,partition_key=PartitionKey(path="/categoryId")
       ,indexing_policy=indexing_policy
       ,offer_throughput=1000 #This sets autoscale throughput (autoscaling between 100 - 1000 RU/s)
    )

    #We can get container if it already exists
    #container = database.get_container_client("products")

    print("New container :",container.id)

    #Update container to enable autoscale
    print(f"Container '{container.id}' updated with autoscale throughput enabled")

    # Creating documents
    documents = [
        {
            "id": "1",
            "productName": "Laptop",
            "categoryId": "Electronics",
            "price": [600,800,1000]
        },
        {
            "id": "2",
            "productName": "Smartphone",
            "categoryId": "Electronics",
            "price": [600,800,1000]
        },
        {
            "id": "3",
            "productName": "Coffee Maker",
            "categoryId": "Home Appliances",
            "price": 80
        },
        {
            "id": "2",
            "productName": "Smartphone in Home Appliances",
            "categoryId": "Home Appliances",
            "price": 18000
        }
    ]

    # Inserting records
    for doc in documents:
        # Query to check if a document with the same 'id' already exists
        query = f"SELECT * FROM products p WHERE p.id = '{doc['id']}' and p.categoryId = '{doc['categoryId']}'"
        existing_items = list(container.query_items(query=query, enable_cross_partition_query=True))
        if existing_items:
            print(f"Document with id {doc['id']} and partition key {doc['categoryId']} already exists. Skipping insertion.")
        else:
            # Insert the document if not already existing
            container.create_item(body=doc)
            print(f"Document with id {doc['id']} and partition key {doc['categoryId']} created successfully!")


    # Prepare documents to insert in bulk
    documents = [
    {"id": str(i), "productName": f"Product {i}", "categoryId": "Electronics", "price": 100 + i}
    for i in range(4, 1001)  # Insert 1000 items
    ]

    # Perform bulk insert
    for doc in documents:
        container.upsert_item(doc)

    print('Bulk insert completed !')

    # Query to get documents where categoryId is 'Electronics'
    query = "SELECT p.productName FROM products p WHERE p.categoryId = 'Home Appliances'"

     # Execute the query
    items = container.query_items(
        query=query,
        enable_cross_partition_query=True  # Enable cross-partition query if needed
    )

    # Print the result
    print("Documents in category 'Electronics':")
    for item in items:
        print(item)

    # Updating the document with productName = "Laptop"
    productName = "Laptop"
    
    # Query the item to update
    query = f"Select * from products p where p.productName = '{productName}'"
    existing_items = list(container.query_items(query=query, enable_cross_partition_query=True))
    print(existing_items)
    if existing_items:
            doc_to_update = existing_items[0] # 0 is to update only the first document.
            # in order to update all documents iterate over the document.
            # for doc_to_update in existing_items

            # Modify the document fields
            doc_to_update['price'] = 5000 # Updating the price
            doc_to_update['productName'] = 'High end laptop' # Updating the laptop name

            # Replace the existing document with updated one
            container.replace_item(item=doc_to_update['id'],body=doc_to_update)
            print(f"Document with id {doc_to_update['id']} updated successfully")
    else:
         print(f"Document with id productName = '{productName}' not found!")

    # Query the updated item
    query = f"Select * from products p where p.productName = 'High end laptop'"
    existing_items = list(container.query_items(query=query, enable_cross_partition_query=True))
    print(existing_items)

    # Deleting the document
    document_id = "2"
    partition_key_value = "Electronics"
    container.delete_item(item=document_id,partition_key=partition_key_value)
    print(f"Document with document_id : {document_id} deleted successfully")

except exceptions.CosmosHttpResponseError as e:
    print(f"Cosmos DB Error: {e.message}")
except exceptions.CosmosResourceNotFoundError:
    print(f"Document with ID {document_id} not found.")
except Exception as e:
    print(f"General Error: {str(e)}")


#First commit
