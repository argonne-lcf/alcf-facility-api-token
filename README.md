# ALCF Facility API Token

This repository contains scripts and documentation to facilitate the generation of Globus access tokens for the ALCF Facility API.

## Quick Virtual Environment

Create and activate a python3 (`>=3.10.7`) environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Generate Access Token

Generate the authentication flow URL with the command below. Copy-paste the URL to your browser, authenticate with your ALCF credentials, and copy-paste the resulting authorization code in your terminal.
```bash
python alcf_facility_api_globus_token.py authenticate
```

The command above generates both an access token and a refresh token, which are stored in your home directory at `~/.globus/app/8b84fc2d-49e9-49ea-b54d-b3a29a70cf31/alcf_facility_api_app/tokens.json`. You can view your access token with:
```bash
python alcf_facility_api_globus_token.py get_access_token
```

You can also export your access token within an environment variable:
```bash
access_token=$(python alcf_facility_api_globus_token.py get_access_token)
```

When using python, you can retrieve your access token with the following:
```python
from alcf_facility_api_globus_token import get_access_token
access_token = get_access_token()
```

While your access token is valid for 48 hours, the `get_access_token` function will automatically refresh your token if your token is expired. Currently, the Facility API application allows the use of refresh tokens for up to 7 days, after which you will need to manually reauthenticate with your ALCF credentials.

## Troubleshooting

* **Permission Denied** (make sure you authenticate with ALCF credentials):
 * Logout from Globus at [https://app.globus.org/logout](https://app.globus.org/logout)
 * Clear browser cache or use an *incognito* browser
 * Reauthenticate with `python alcf_facility_api_globus_token.py authenticate`
* **IdentityMismatchError: Detected a change in identity**:
 * This happens when trying to get an access token using a Globus identity that is not linked to the one you previously used to generate your access tokens. Locate your tokens file (typically at `~/.globus/app/8b84fc2d-49e9-49ea-b54d-b3a29a70cf31/alcf_facility_api_app/tokens.json`), delete it, and restart the authentication process.