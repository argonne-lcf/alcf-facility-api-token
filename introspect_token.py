import os
import globus_sdk
from alcf_facility_api_globus_token import get_access_token
from dotenv import load_dotenv
load_dotenv()

# Load your Globus service account client credentials
CLIENT_ID = os.getenv("GLOBUS_SERVICE_API_CLIENT_ID", None)
CLIENT_SECRET = os.getenv("GLOBUS_SERVICE_API_CLIENT_SECRET", None)

# Create an SDK client using the service account credentials
print("\nCreating Globus SDK client using credentials ...")
client = globus_sdk.ConfidentialAppAuthClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# Get existing access token
access_token = get_access_token()

# Prepare introspection data
data = {
    "token": access_token,
    "include": "session_info,identity_set_detail",
    "authentication_policies": "a128e981-c9a5-417a-97ab-8571c9831bff"
}


# Introspect token with Globus Auth
introspection = client.post(
    "/v2/oauth2/token/introspect",
    data=data, 
    encoding="form",
)

# Display introspection on the terminal
print("\nToken introspection data")
print("------------------------")
print(introspection)