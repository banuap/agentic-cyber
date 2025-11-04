import json
import requests
from google.adk.agents.llm_agent import Agent

MCP_SSE_URL = 'http://localhost:3000/mcp/sse'
MCP_QUERY_URL = 'http://localhost:3000/mcp/query'

def get_mongodb_connection_info() -> dict:
    """Returns the MongoDB connection information for the application."""
    return {
        "status": "success",
        "host": "34.172.211.78",
        "port": 27017,
        "database": "app_auth",
        "connection_string": "mongodb://34.172.211.78:27017/app_auth"
    }

def fetch_user_data_from_mcp() -> dict:
    """Fetches user data from MongoDB via the MCP server."""
    try:
        response = requests.post(MCP_QUERY_URL, json={'query': 'get_user_data'})
        response.raise_for_status()
        
        users = response.json()
        
        # Extract schema information from the first user
        if users:
            schema = {
                'identityAttribute': 'userId',
                'displayAttribute': 'email',
                'attributes': list(users[0].keys())
            }
            
            # Extract unique roles (entitlements)
            all_roles = [role for user in users for role in user.get('roles', [])]
            entitlements = list(set(all_roles))
            
            return {
                "status": "success",
                "user_count": len(users),
                "users": users,
                "schema": schema,
                "entitlements": entitlements
            }
        else:
            return {
                "status": "success",
                "user_count": 0,
                "users": [],
                "schema": {},
                "entitlements": []
            }
    
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to fetch user data: {str(e)}"
        }

def generate_sailpoint_onboarding_form() -> dict:
    """Generates the complete SailPoint application onboarding form with all required fields."""
    connection_info = get_mongodb_connection_info()
    user_data = fetch_user_data_from_mcp()
    
    if user_data["status"] == "error":
        return user_data
    
    sailpoint_form = {
        "application_details": {
            "application_name": "MongoDB Authorization App",
            "application_owner": "IT Security Team",
            "description": "Application using MongoDB for user authorization and role management",
            "application_type": "Directly Connected"
        },
        "connection_details": {
            "connector_type": "JDBC Connector",
            "host": connection_info["host"],
            "port": connection_info["port"],
            "database": connection_info["database"],
            "jdbc_url": connection_info["connection_string"],
            "authentication": "No authentication (development environment)"
        },
        "schema_mapping": {
            "identity_attribute": user_data["schema"].get("identityAttribute", "userId"),
            "display_attribute": user_data["schema"].get("displayAttribute", "email"),
            "account_attributes": user_data["schema"].get("attributes", []),
            "entitlement_attribute": "roles"
        },
        "entitlements": {
            "discovered_roles": user_data["entitlements"],
            "entitlement_type": "Multi-valued attribute"
        },
        "account_correlation": {
            "correlation_rule": "Match by email address",
            "correlation_attribute": "email"
        },
        "provisioning_policy": {
            "create_account": "Enabled",
            "update_account": "Enabled",
            "delete_account": "Enabled",
            "manage_entitlements": "Enabled"
        },
        "aggregation_info": {
            "total_accounts": user_data["user_count"],
            "sample_accounts": user_data["users"][:3] if user_data["users"] else []
        }
    }
    
    return {
        "status": "success",
        "sailpoint_onboarding_form": sailpoint_form
    }

# Create the ADK agent
root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='sailpoint_onboarding_agent',
    description="An agent that helps onboard applications to SailPoint by connecting to MongoDB via an MCP server.",
    instruction="""You are a SailPoint application onboarding specialist. Your job is to help users onboard applications to SailPoint Identity Security Cloud.

When a user asks you to prepare the onboarding form or get application details:
1. Use the 'get_mongodb_connection_info' tool to get the database connection details
2. Use the 'fetch_user_data_from_mcp' tool to retrieve user data and discover the schema
3. Use the 'generate_sailpoint_onboarding_form' tool to create a complete onboarding form

Present the information in a clear, structured format that can be used to fill out the SailPoint application onboarding form.""",
    tools=[get_mongodb_connection_info, fetch_user_data_from_mcp, generate_sailpoint_onboarding_form],
)