import os
from azure.cosmos import CosmosClient, ThroughputProperties, database, exceptions
from azure.cosmos.partition_key import PartitionKey

# Cosmos DB connection details
endpoint = "https://cosmosdbact1018.documents.azure.com:443/"
key = "OQY7aYAH1hjjfOpWl6DJUlMzH2QtHPWvq4QuP0W5UByYfpWxcTcNfCxwFQfG90OIS36EPCQze7CtACDbAdm5ag=="

# Initialize the Cosmos client
client = CosmosClient(endpoint, key)

try:
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
    database = client.create_database_if_not_exists("cosmosworks")
    print("New Database ID: ", database.id)

    #Creating Container with autoscale
    container = database.create_container_if_not_exists(
        id="products"
       ,partition_key=PartitionKey(path="/categoryId")
       ,offer_throughput=1000 #This sets autoscale throughput (autoscaling between 100 - 1000 RU/s)
    )

    print("New container :",container.id)

    #Setting autoscale throughput using dictionary
    #throughput_settings = {
    #    "resource":{
    #        "resourceId": container.id
    #        ,"maxThroughput": 4000
    #        ,"isAutoscaleEnabled" : True
    #        }
    #    }

    #Update container to enable autoscale
    print(f"Container '{container.id}' updated with autoscale throughput enabled")

except exceptions.CosmosHttpResponseError as e:
    print(f"Cosmos DB Error: {e.message}")
except Exception as e:
    print(f"General Error: {str(e)}")

#First commit
