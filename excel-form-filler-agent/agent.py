import json
import requests
import openpyxl
from openpyxl.utils import get_column_letter
from pathlib import Path
from datetime import datetime
from typing import Optional
from google.adk.agents.llm_agent import Agent

MCP_QUERY_URL = 'http://34.9.116.130:3000/mcp/query'
DEFAULT_TEMPLATE = r'/mnt/c/Users/banu.parasuraman/Downloads/SailPoint_Onboarding_Application_Questionnaire_v2.xlsx'

def get_sailpoint_data_from_mcp() -> dict:
    """Fetches SailPoint onboarding data from the MCP server."""
    try:
        response = requests.post(MCP_QUERY_URL, json={'query': 'get_user_data'})
        response.raise_for_status()
        
        users = response.json()
        
        # Extract schema information
        if users:
            schema = {
                'identityAttribute': 'userId',
                'displayAttribute': 'email',
                'attributes': list(users[0].keys())
            }
            
            # Extract unique roles
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

def fill_excel_form(template_path: str = DEFAULT_TEMPLATE, output_path: Optional[str] = None) -> dict:
    """
    Fills the SailPoint onboarding Excel form with data from MCP server.
    
    Args:
        template_path: Path to the Excel template file
        output_path: Path where the filled Excel file should be saved
    
    Returns:
        Dictionary with status and details of the operation
    """
    try:
        # Check if template exists
        if not Path(template_path).exists():
            return {
                "status": "error",
                "message": f"Template file not found: {template_path}"
            }
        
        # Get data from MCP server
        data = get_sailpoint_data_from_mcp()
        
        if data["status"] == "error":
            return data
        
        # Load the Excel template
        wb = openpyxl.load_workbook(template_path)
        
        # Fill Application General Information sheet
        if 'Application General Information' in wb.sheetnames:
            ws = wb['Application General Information']
            
            # Application Name
            ws['C12'] = "MongoDB Authorization App"
            
            # Application Description  
            ws['C19'] = "MongoDB-based application managing user authorization, roles, and permissions for internal systems."
            
            # Submitted By
            ws['D21'] = "Automated Agent"
            
            # Business Owner
            ws['C25'] = "IT Security Team"
            
            # Technical Owner
            ws['C26'] = "Database Administrator"
            
            # Lead Technical Contact
            ws['C27'] = "MongoDB Team"
            
            # Internally developed or procured
            ws['C29'] = "Internally Developed"
            
            # Environments
            ws['C30'] = "DEV, UAT, PROD"
            
            # Domain
            ws['C31'] = "CWS"
            
            # Business Objectives
            ws['C32'] = "Centralized user access management and role-based authorization"
            
            # SOW Required
            ws['C33'] = "No"
            
            # Total active users
            ws['C34'] = str(data.get('user_count', 0))
            
            # Uses Entra/AD
            ws['C35'] = "No - uses MongoDB for authentication"
            
            # Current provisioning process
            ws['C36'] = "Manual - Database updates"
            
            # Account creation process
            ws['C37'] = "Direct MongoDB document insertion with role assignment"
            
            # Account types
            ws['C38'] = "Employee, Contractor"
            
            # Total roles
            ws['C39'] = f"{len(data.get('entitlements', []))} roles: {', '.join(data.get('entitlements', []))}"
            
            # Multiple roles
            ws['C40'] = "Yes"
            
            # Elevated privileges
            ws['C41'] = "Admin role provides elevated access to system configuration"
            
            # RBAC
            ws['C42'] = "Yes - role-based access controls implemented"
            
            # Super admin
            ws['C43'] = "Yes - 'admin' role has full system access"
            
            # SOD Policies
            ws['C44'] = "Yes - admin and user roles have separation"
        
        # Fill Application On-boarding Form sheet
        if 'Application On-boarding Form' in wb.sheetnames:
            ws = wb['Application On-boarding Form']
            
            # Case sensitive
            ws['C13'] = "Yes"
            
            # Authorized to change
            ws['C14'] = "Database Administrator"
            
            # Disabled accounts
            ws['C15'] = "Yes - status='inactive'"
            
            # Dormant accounts
            ws['C16'] = "Yes - via status field"
            
            # Service accounts
            ws['C17'] = "Yes - MongoDB connection credentials"
            
            # Password rotation
            ws['C18'] = "Quarterly"
            
            # Business Owner
            ws['C20'] = "IT Security Team"
            
            # Attribute Name
            ws['C21'] = "userId, firstName, lastName, email, status, roles"
        
        # Fill Environment sheet
        if 'Environment' in wb.sheetnames:
            ws = wb['Environment']
            
            # Production Details
            ws['G13'] = "34.172.211.78"  # Hostname
            ws['G14'] = "27017"  # Port
            ws['G15'] = "app_auth"  # Database Name
            ws['G16'] = "sailpoint_readonly"  # Username (placeholder)
            ws['G17'] = "[Stored in Secrets Manager]"  # Password
            ws['G18'] = "mongodb://34.172.211.78:27017/app_auth"  # JDBC/Connection URL
            
            # API Details
            ws['G23'] = "http://34.9.116.130:3000"  # Base URL (MCP Server)
        
        # Fill Process type sheet
        if 'Process type ' in wb.sheetnames:
            ws = wb['Process type ']
            
            # Create account
            ws['B3'] = "Yes"
            ws['C3'] = "Create user document in MongoDB with required attributes and roles"
            
            # Modify account
            ws['B4'] = "Yes"
            ws['C4'] = "Update user document fields including roles array"
            
            # Disable account
            ws['B5'] = "Yes"
            ws['C5'] = "Set status field to 'inactive'"
            
            # Delete account
            ws['B6'] = "Yes"
            ws['C6'] = "Remove user document from collection"
            
            # Required attributes
            ws['B7'] = "userId, firstName, lastName, email, status, roles[]"
        
        # Fill Roles sheet
        if 'Roles' in wb.sheetnames:
            ws = wb['Roles']
            
            # Fill production roles
            roles_data = data.get('entitlements', [])
            start_row = 2
            for idx, role in enumerate(roles_data, start=1):
                ws[f'G{start_row + idx}'] = idx  # S.no
                ws[f'H{start_row + idx}'] = role  # Role Name
                ws[f'I{start_row + idx}'] = f"{role} permissions"  # Entitlement
                ws[f'J{start_row + idx}'] = f"Standard {role} role"  # Description
        
        # Generate output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(__file__).parent
            output_path = output_dir / f"SailPoint_Onboarding_Filled_{timestamp}.xlsx"
        
        # Save the filled workbook
        wb.save(str(output_path))
        wb.close()
        
        return {
            "status": "success",
            "message": f"Excel form filled successfully and saved to: {output_path}",
            "output_file": str(output_path),
            "total_accounts": data["user_count"],
            "entitlements": data["entitlements"],
            "filled_sheets": ["Application General Information", "Application On-boarding Form", "Environment", "Process type ", "Roles"]
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error filling Excel form: {str(e)}"
        }

def read_excel_form(file_path: str) -> dict:
    """
    Reads the filled SailPoint onboarding Excel form and returns the data.
    
    Args:
        file_path: Path to the Excel file to read
    
    Returns:
        Dictionary containing all the form data
    """
    try:
        if not Path(file_path).exists():
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }
        
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        
        form_data = {
            "application_details": {
                "application_name": ws['B4'].value,
                "application_owner": ws['B5'].value,
                "description": ws['B6'].value,
                "application_type": ws['B7'].value
            },
            "connection_details": {
                "connector_type": ws['B9'].value,
                "host": ws['B10'].value,
                "port": ws['B11'].value,
                "database": ws['B12'].value,
                "jdbc_url": ws['B13'].value,
                "authentication": ws['B14'].value
            },
            "schema_mapping": {
                "identity_attribute": ws['B16'].value,
                "display_attribute": ws['B17'].value,
                "account_attributes": ws['B18'].value,
                "entitlement_attribute": ws['B19'].value
            },
            "entitlements": {
                "discovered_roles": ws['B21'].value,
                "entitlement_type": ws['B22'].value
            },
            "account_correlation": {
                "correlation_rule": ws['B24'].value,
                "correlation_attribute": ws['B25'].value
            },
            "provisioning_policy": {
                "create_account": ws['B27'].value,
                "update_account": ws['B28'].value,
                "delete_account": ws['B29'].value,
                "manage_entitlements": ws['B30'].value
            },
            "aggregation_info": {
                "total_accounts": ws['B32'].value,
                "sample_account_1": ws['B33'].value,
                "sample_account_2": ws['B34'].value,
                "sample_account_3": ws['B35'].value
            }
        }
        
        return {
            "status": "success",
            "form_data": form_data
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading Excel form: {str(e)}"
        }

# Create the Excel Form Filler Agent
root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='excel_form_filler_agent',
    description="An agent that fills SailPoint onboarding Excel forms with data from MongoDB via MCP server.",
    instruction="""You are an Excel form automation specialist for SailPoint application onboarding.

When a user asks you to fill the Excel form:
1. Use 'fill_excel_form' tool - it will automatically fetch data from MCP/MongoDB and fill all fields
2. The tool fills 5 sheets: Application General Information, Application On-boarding Form, Environment, Process type, and Roles
3. Provide a clear summary of what was filled and where the file was saved

When a user asks to read a filled form:
1. Use 'read_excel_form' tool with the file path
2. Present the data in a clear, organized format

When a user asks for raw MongoDB data:
1. Use 'get_sailpoint_data_from_mcp' tool

The template is automatically located at:
C:\\Users\\banu.parasuraman\\Downloads\\SailPoint_Onboarding_Application_Questionnaire_v2.xlsx

Output files are saved in the excel-form-filler-agent directory with a timestamp.""",
    tools=[fill_excel_form, read_excel_form, get_sailpoint_data_from_mcp],
)
