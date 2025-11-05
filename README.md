# SailPoint App Onboarding with MCP Server

This project demonstrates an automated SailPoint application onboarding workflow using a MongoDB database, an MCP (Model Context Protocol) server, and a Google ADK agent.

## Architecture

```
┌─────────────────────────────┐
│  MongoDB on GKE             │
│  IP: 34.172.211.78          │
│  Namespace: sailpoint       │
└──────────┬──────────────────┘
           │ (internal K8s service)
           │
┌──────────▼──────────────────┐
│  MCP Server on GKE          │
│  IP: 34.9.116.130           │
│  Namespace: sailpoint       │
│  Ports: 3000 (SSE + REST)   │
└──────────┬──────────────────┘
           │ (external access)
           │
┌──────────▼──────────────────┐
│  Python ADK Agent           │
│  (Local or Cloud)           │
│  - Connects via HTTP        │
│  - Fetches MongoDB data     │
│  - Generates SailPoint form │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  SailPoint Onboarding Form  │
│  - Application Details      │
│  - Connection Info          │
│  - Schema Mapping           │
│  - Entitlements             │
└─────────────────────────────┘
```

## Components

### 1. MongoDB on GKE
- **Location**: Google Kubernetes Engine cluster
- **Database**: `app_auth`
- **Collection**: `users` (contains user accounts and roles)
- **External IP**: `34.172.211.78:27017`
- **Internal Service**: `mongodb-service.sailpoint.svc.cluster.local:27017`
- **Namespace**: `sailpoint`

### 2. MCP Server (Node.js) on GKE
- **Purpose**: Acts as a middleware between MongoDB and the agent
- **Deployment**: Containerized on GKE using Artifact Registry
- **External IP**: `34.9.116.130:3000`
- **Features**:
  - Server-Sent Events (SSE) endpoint for real-time updates
  - REST API for querying MongoDB data
- **Endpoints**:
  - `GET /mcp/sse` - SSE connection endpoint
  - `POST /mcp/query` - Query endpoint for fetching data
- **Docker Image**: `us-central1-docker.pkg.dev/sparkle-labs-310106/mcp-server/mcp-server:latest`

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
cd c:\Users\banu.parasuraman\Downloads\agentic-cyber

# Create namespace
kubectl apply -f sailpoint-namespace.yaml

# Deploy MongoDB
kubectl apply -f mongodb-deployment.yaml
kubectl apply -f mongodb-service.yaml
```

Verify MongoDB is running:
```bash
kubectl get pods -n sailpoint
kubectl get services -n sailpoint
```

### 2. Build and Deploy MCP Server to GKE

```bash
cd mcp-server

# Build Docker image
docker build -t us-central1-docker.pkg.dev/sparkle-labs-310106/mcp-server/mcp-server:latest .

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Push image to Artifact Registry
docker push us-central1-docker.pkg.dev/sparkle-labs-310106/mcp-server/mcp-server:latest

# Deploy to GKE
cd ..
kubectl apply -f mcp-server-deployment.yaml
kubectl apply -f mcp-server-service.yaml
```

Verify MCP server is running:
```bash
kubectl get pods -n sailpoint
kubectl get services -n sailpoint

# Test the SSE endpoint (replace with your external IP)
curl -N http://34.9.116.130:3000/mcp/sse
```

### 3. Configure and Run the ADK Agent

```bash
cd python-adk-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment variables in .env file
# Make sure GOOGLE_API_KEY is set or use Vertex AI authentication

# Run the agent
adk run agent.py
```

**Note**: The agent is already configured to connect to the MCP server at `http://34.9.116.130:3000`. If your external IP is different, update the URLs in `agent.py`.

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
├── mongodb-deployment.yaml           # MongoDB Kubernetes deployment
├── mongodb-service.yaml              # MongoDB service (LoadBalancer)
├── sailpoint-namespace.yaml          # Kubernetes namespace definition
├── mcp-server-deployment.yaml        # MCP Server Kubernetes deployment
├── mcp-server-service.yaml           # MCP Server service (LoadBalancer)
├── mcp-server/                       # MCP Server (Node.js)
│   ├── package.json
│   ├── index.js
│   └── Dockerfile                    # Docker configuration for GKE
└── python-adk-agent/                 # ADK Agent (Python)
    ├── requirements.txt
    ├── agent.py
    ├── __init__.py
    └── .env                          # Environment configuration
```

## Deployed Services

| Service | Type | Internal Address | External IP | Port |
|---------|------|------------------|-------------|------|
| MongoDB | LoadBalancer | mongodb-service.sailpoint.svc.cluster.local | 34.172.211.78 | 27017 |
| MCP Server | LoadBalancer | mcp-server-service.sailpoint.svc.cluster.local | 34.9.116.130 | 3000 |

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
