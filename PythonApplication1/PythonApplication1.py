import os
from azure.cosmos import CosmosClient, exceptions

# Cosmos DB connection details
endpoint = "https://cosmosdbact1018.documents.azure.com:443/"
key = "OQY7aYAH1hjjfOpWl6DJUlMzH2QtHPWvq4QuP0W5UByYfpWxcTcNfCxwFQfG90OIS36EPCQze7CtACDbAdm5ag=="

# Initialize the Cosmos client
client = CosmosClient(endpoint, key)

try:
    # Get database account properties
    account_properties = client.get_database_account()
    print("Account Endpoint:", account_properties.DatabasesLink)
except exceptions.CosmosHttpResponseError as e:
    print(f"Cosmos DB Error: {e.message}")
except Exception as e:
    print(f"General Error: {str(e)}")

