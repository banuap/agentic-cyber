# SailPoint App Onboarding with MCP Server

This project demonstrates an automated SailPoint application onboarding workflow using a MongoDB database, an MCP (Model Context Protocol) server, and a Google ADK agent.

## Architecture

```
┌─────────────────┐     ┌─────────────┐     ┌──────────────────┐
│  MongoDB (GKE)  │────▶│ MCP Server  │────▶│  ADK Agent       │
│                 │     │  (Node.js)  │     │  (Python)        │
└─────────────────┘     └─────────────┘     └──────────────────┘
                              │                       │
                              │                       ▼
                              │              ┌──────────────────┐
                              │              │  SailPoint       │
                              └─────────────▶│  Onboarding Form │
                                             └──────────────────┘
```

## Components

### 1. MongoDB on GKE
- **Location**: Google Kubernetes Engine cluster
- **Database**: `app_auth`
- **Collection**: `users` (contains user accounts and roles)
- **External IP**: Exposed via LoadBalancer service

### 2. MCP Server (Node.js)
- **Purpose**: Acts as a middleware between MongoDB and the agent
- **Features**:
  - Server-Sent Events (SSE) endpoint for real-time updates
  - REST API for querying MongoDB data
- **Endpoints**:
  - `GET /mcp/sse` - SSE connection endpoint
  - `POST /mcp/query` - Query endpoint for fetching data

### 3. ADK Agent (Python)
- **Purpose**: Automates the SailPoint application onboarding process
- **Tools**:
  - `get_mongodb_connection_info()` - Retrieves connection details
  - `fetch_user_data_from_mcp()` - Fetches user data and schema
  - `generate_sailpoint_onboarding_form()` - Generates complete onboarding form

## Prerequisites

- Google Cloud Platform account with GKE cluster
- `kubectl` configured to connect to your GKE cluster
- Node.js (v14+)
- Python (v3.8+)
- Google ADK installed (`pip install google-adk`)
- MongoDB Compass (optional, for database management)

## Setup Instructions

### 1. Deploy MongoDB to GKE

```bash
cd agentic-cyber
kubectl apply -f sailpoint-namespace.yaml
kubectl apply -f mongodb-deployment.yaml
kubectl apply -f mongodb-service.yaml
```

Verify MongoDB is running:
```bash
kubectl get pods -n sailpoint
kubectl get services -n sailpoint
```

### 2. Start the MCP Server

```bash
cd mcp-server
npm install
npm start
```

The server will run on `http://localhost:3000`

Test the SSE endpoint:
```bash
curl -N http://localhost:3000/mcp/sse
```

### 3. Run the ADK Agent

```bash
cd python-adk-agent
pip install -r requirements.txt
adk run agent.py
```

## Usage

Once the agent is running, you can interact with it using natural language:

- "Please generate the SailPoint onboarding form"
- "What are the connection details for the MongoDB database?"
- "Show me the user data and schema information"

The agent will use its tools to fetch data from the MCP server and present a structured SailPoint onboarding form.

## SailPoint Onboarding Form Fields

The generated form includes:

### Application Details
- Application Name
- Application Owner
- Description
- Application Type

### Connection Details
- Connector Type (JDBC)
- Host, Port, Database
- JDBC Connection String
- Authentication Method

### Schema Mapping
- Identity Attribute (userId)
- Display Attribute (email)
- Account Attributes
- Entitlement Attribute (roles)

### Entitlements
- Discovered Roles (admin, user, guest)
- Entitlement Type

### Account Correlation
- Correlation Rule
- Correlation Attribute

### Provisioning Policy
- Create/Update/Delete Account settings
- Entitlement Management

## Project Structure

```
agentic-cyber/
├── mongodb-deployment.yaml      # MongoDB Kubernetes deployment
├── mongodb-service.yaml         # MongoDB service (LoadBalancer)
├── sailpoint-namespace.yaml     # Kubernetes namespace definition
├── mcp-server/                  # MCP Server (Node.js)
│   ├── package.json
│   └── index.js
└── python-adk-agent/            # ADK Agent (Python)
    ├── requirements.txt
    ├── agent.py
    ├── __init__.py
    └── .env
```

## Security Notes

⚠️ **Important**: This is a development/demo environment:
- MongoDB is deployed without authentication
- The database is exposed with a public IP
- API keys are stored in `.env` files

For production use:
- Enable MongoDB authentication
- Use Kubernetes secrets for credentials
- Implement network policies
- Use private IPs or VPN connections
- Rotate API keys regularly

## License

MIT
