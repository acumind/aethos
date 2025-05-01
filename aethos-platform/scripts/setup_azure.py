#!/usr/bin/env python
"""
Script to set up required Azure resources for the application.

This script creates:
1. Resource Group (if not exists)
2. Azure SQL Database
3. Azure Blob Storage Account
4. Azure OpenAI Service
5. Azure AI Agent Service
"""

from app.core.config import settings
from azure.core.exceptions import ResourceExistsError
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
import os
import sys
import argparse
import logging
from typing import Dict, Any

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_credential():
    """Get Azure credential."""
    try:
        credential = DefaultAzureCredential()
        return credential
    except Exception as e:
        logger.error(f"Error getting Azure credential: {str(e)}")
        logger.info("Please run 'az login' to authenticate with Azure CLI")
        sys.exit(1)


def create_resource_group(credential, subscription_id: str, resource_group: str, location: str):
    """Create Azure Resource Group if it doesn't exist."""
    client = ResourceManagementClient(credential, subscription_id)

    # Check if resource group exists
    if client.resource_groups.check_existence(resource_group):
        logger.info(f"Resource Group '{resource_group}' already exists")
        return

    # Create resource group
    logger.info(f"Creating Resource Group '{resource_group}' in {location}...")
    result = client.resource_groups.create_or_update(
        resource_group,
        {"location": location}
    )
    logger.info(f"Resource Group '{result.name}' created successfully")


def create_sql_server_and_database(credential, subscription_id: str, resource_group: str,
                                   location: str, server_name: str, db_name: str,
                                   admin_user: str, admin_password: str):
    """Create Azure SQL Server and Database."""
    client = SqlManagementClient(credential, subscription_id)

    # Check if server exists
    server_exists = False
    try:
        server = client.servers.get(resource_group, server_name)
        server_exists = True
        logger.info(f"SQL Server '{server_name}' already exists")
    except Exception:
        server_exists = False

    # Create server if it doesn't exist
    if not server_exists:
        logger.info(f"Creating SQL Server '{server_name}'...")
        server_params = {
            'location': location,
            'administrator_login': admin_user,
            'administrator_login_password': admin_password,
            'version': '12.0'
        }
        server = client.servers.begin_create_or_update(
            resource_group,
            server_name,
            server_params
        ).result()
        logger.info(f"SQL Server '{server.name}' created successfully")

    # Create firewall rule to allow Azure services
    try:
        logger.info("Adding firewall rule to allow Azure services...")
        client.firewall_rules.create_or_update(
            resource_group,
            server_name,
            "AllowAllAzureIPs",
            {
                "start_ip_address": "0.0.0.0",
                "end_ip_address": "0.0.0.0"
            }
        )
        logger.info("Firewall rule added successfully")
    except Exception as e:
        logger.warning(f"Error adding firewall rule: {str(e)}")

    # Check if database exists
    db_exists = False
    try:
        db = client.databases.get(resource_group, server_name, db_name)
        db_exists = True
        logger.info(f"SQL Database '{db_name}' already exists")
    except Exception:
        db_exists = False

    # Create database if it doesn't exist
    if not db_exists:
        logger.info(f"Creating SQL Database '{db_name}'...")
        db_params = {
            'location': location,
            'sku': {
                'name': 'Basic'
            }
        }
        db = client.databases.begin_create_or_update(
            resource_group,
            server_name,
            db_name,
            db_params
        ).result()
        logger.info(f"SQL Database '{db.name}' created successfully")

    # Get connection string
    connection_string = f"Server=tcp:{server_name}.database.windows.net,1433;Database={db_name};User ID={admin_user}@{server_name};Password={admin_password};Encrypt=true;Connection Timeout=30;"
    return connection_string


def create_storage_account(credential, subscription_id: str, resource_group: str,
                           location: str, storage_name: str):
    """Create Azure Storage Account and Container."""
    client = StorageManagementClient(credential, subscription_id)

    # Check if storage account exists
    storage_exists = False
    try:
        storage = client.storage_accounts.get_properties(
            resource_group, storage_name)
        storage_exists = True
        logger.info(f"Storage Account '{storage_name}' already exists")
    except Exception:
        storage_exists = False

    # Create storage account if it doesn't exist
    if not storage_exists:
        logger.info(f"Creating Storage Account '{storage_name}'...")
        storage_params = {
            'location': location,
            'kind': 'StorageV2',
            'sku': {
                'name': 'Standard_LRS'
            }
        }
        storage = client.storage_accounts.begin_create(
            resource_group,
            storage_name,
            storage_params
        ).result()
        logger.info(f"Storage Account '{storage.name}' created successfully")

    # Get storage keys
    keys = client.storage_accounts.list_keys(resource_group, storage_name)
    storage_key = keys.keys[0].value

    # Get connection string
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_name};AccountKey={storage_key};EndpointSuffix=core.windows.net"

    return connection_string


def create_cognitive_services(credential, subscription_id: str, resource_group: str,
                              location: str, service_name: str, kind: str, sku: str):
    """Create Azure Cognitive Services account."""
    client = CognitiveServicesManagementClient(credential, subscription_id)

    # Check if account exists
    service_exists = False
    try:
        service = client.accounts.get(resource_group, service_name)
        service_exists = True
        logger.info(f"Cognitive Service '{service_name}' already exists")
    except Exception:
        service_exists = False

    # Create account if it doesn't exist
    if not service_exists:
        logger.info(f"Creating Cognitive Service '{service_name}'...")
        account_params = {
            'location': location,
            'kind': kind,
            'sku': {
                'name': sku
            },
            'properties': {}
        }
        service = client.accounts.begin_create(
            resource_group,
            service_name,
            account_params
        ).result()
        logger.info(f"Cognitive Service '{service.name}' created successfully")

    # Get keys
    keys = client.accounts.list_keys(resource_group, service_name)
    service_key = keys.key1

    # Get endpoint
    endpoint = f"https://{location}.api.cognitive.microsoft.com/"

    return endpoint, service_key


def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(
        description="Set up Azure resources for the application")
    parser.add_argument("--location", default="eastus",
                        help="Azure region to create resources in")
    parser.add_argument("--sql-admin", default="sqladmin",
                        help="SQL Server admin username")
    parser.add_argument("--sql-password", help="SQL Server admin password")
    parser.add_argument("--resource-prefix",
                        help="Prefix for resource names", default="aiagent")

    args = parser.parse_args()

    # Get Azure credentials
    credential = get_credential()

    # Get configuration from settings or command line
    subscription_id = settings.AZURE_SUBSCRIPTION_ID
    resource_group = settings.AZURE_RESOURCE_GROUP
    location = args.location
    resource_prefix = args.resource_prefix

    # Generate resource names
    sql_server_name = f"{resource_prefix}sql"
    sql_db_name = f"{resource_prefix}db"
    storage_name = f"{resource_prefix}storage"
    openai_name = f"{resource_prefix}openai"
    ai_agent_name = f"{resource_prefix}aiagent"

    # Get SQL admin credentials
    sql_admin = args.sql_admin
    sql_password = args.sql_password

    if not sql_password:
        # If password not provided, generate a secure one
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        sql_password = ''.join(secrets.choice(alphabet) for i in range(16))
        logger.info(f"Generated SQL admin password: {sql_password}")

    try:
        # Create resource group
        create_resource_group(credential, subscription_id,
                              resource_group, location)

        # Create SQL Server and Database
        connection_string = create_sql_server_and_database(
            credential, subscription_id, resource_group, location,
            sql_server_name, sql_db_name, sql_admin, sql_password
        )

        # Create Storage Account
        storage_connection_string = create_storage_account(
            credential, subscription_id, resource_group, location, storage_name
        )

        # Create Azure OpenAI Service
        openai_endpoint, openai_key = create_cognitive_services(
            credential, subscription_id, resource_group, location,
            openai_name, "OpenAI", "S0"
        )

        # Create Azure AI Agent Service (this is a placeholder - as of 2024, there might not be a dedicated ARM API for this)
        # This would typically be done through the Azure portal or CLI
        ai_agent_endpoint = f"https://{ai_agent_name}.cognitiveservices.azure.com/"

        # Update .env file if it exists or create a new one
        env_file = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), ".env")
        env_exists = os.path.exists(env_file)

        env_vars = {}
        if env_exists:
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value

        # Update environment variables
        env_vars["AZURE_SQL_SERVER"] = f"{sql_server_name}.database.windows.net"
        env_vars["AZURE_SQL_DATABASE"] = sql_db_name
        env_vars["AZURE_SQL_USERNAME"] = sql_admin
        env_vars["AZURE_SQL_PASSWORD"] = sql_password
        env_vars["AZURE_STORAGE_CONNECTION_STRING"] = storage_connection_string
        env_vars["AZURE_OPENAI_ENDPOINT"] = openai_endpoint
        env_vars["AZURE_OPENAI_API_KEY"] = openai_key
        env_vars["AZURE_AI_AGENT_SERVICE_ENDPOINT"] = ai_agent_endpoint

        # Write updated .env file
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        logger.info(f"Environment variables updated in {env_file}")
        logger.info("Azure resources set up successfully")

    except Exception as e:
        logger.error(f"Error setting up Azure resources: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
