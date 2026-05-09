# ALCF Facility API Token

This repository contains scripts and documentation to facilitate the generation of Globus access tokens for the ALCF Facility API. 

**Access**: Currently, the ALCF IRI API is available to all ALCF users.

## Quick Start

### 1. Setup Your Environment

Create and activate a Python 3 (`>=3.10.7`) virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Get the Helper Script

Either clone this repository, or download the script directly:

```bash
wget https://raw.githubusercontent.com/argonne-lcf/alcf-facility-api-token/refs/heads/main/alcf_facility_api_globus_token.py
```

### 3. Authenticate

Generate the authentication flow URL with the command below. Copy-paste the URL to your browser, authenticate with your ALCF credentials, and copy-paste the resulting authorization code in your terminal.

```bash
python alcf_facility_api_globus_token.py authenticate
```

The command above generates both an access token and a refresh token, stored at `~/.globus/app/8b84fc2d-49e9-49ea-b54d-b3a29a70cf31/alcf_facility_api_app/tokens.json`.

**Token Validity**: Access tokens are valid for 48 hours. The `get_access_token` command will automatically refresh your token if it has expired. Refresh tokens are valid for 7 days, after which you will need to manually reauthenticate with your ALCF credentials.

### 4. Retrieve Your Access Token

You can retrieve your token in several ways:

**Bash**:
```bash
python alcf_facility_api_globus_token.py get_access_token
```

**Environment variable**:
```bash
access_token=$(python alcf_facility_api_globus_token.py get_access_token)
```

**Python**:
```python
from alcf_facility_api_globus_token import get_access_token
access_token = get_access_token()
```

## API Usage Examples

All examples below use the Python `requests` library. Make sure to execute the following before each example.

```python
import requests
from alcf_facility_api_globus_token import get_access_token

access_token = get_access_token()
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
```

Discover available resources through the `/status/resources` endpoint.
```python
response = requests.get("https://api.alcf.anl.gov/api/v1/status/resources")

print(response.status_code)
print(response.json())
```

### 1. Compute

#### 1.1. Submit a Job

Submits a new job to the scheduler on the target compute resource.

```python
# Polaris
resource_id = "55c1c993-1124-47f9-b823-514ba3849a9a"

# This block is equivalent to the body of a `qsub` script (excluding `#PBS` directives)
commands = "echo Start; sleep 10; echo End"

# Submit to IRI API
response = requests.post(
    f"https://api.alcf.anl.gov/api/v1/compute/job/{resource_id}",
    json={
        "executable": "/bin/bash",
        "arguments": ["-lc", commands],
        "name": "my_job",
        "stdout_path": "/home/<username>/logs",
        "stderr_path": "/home/<username>/logs",
        "resources": {
            "memory": 2222,
            "node_count": 1
        },
        "attributes": {
            "duration": 300,
            "queue_name": "debug",
            "account": "<project_account>",
            "custom_attributes": {"filesystems": "eagle"}
        }
    },
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 1.2. List Jobs

Returns a paginated list of jobs on the target resource. Set `historical` to `true` to include completed jobs.

```python
# Polaris
resource_id = "55c1c993-1124-47f9-b823-514ba3849a9a"

# Submit to IRI API
response = requests.post(
    f"https://api.alcf.anl.gov/api/v1/compute/status/{resource_id}",
    params={
        "historical": "false",
        "limit": 10,
        "offset": 0
    },
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 1.3. Get a Specific Job

Returns the status and details of a single job by its ID. Set `historical` to `true` if the job has already completed.

```python
# Polaris
resource_id = "55c1c993-1124-47f9-b823-514ba3849a9a"
job_id = "<job_id>"

# Submit to IRI API
response = requests.get(
    f"https://api.alcf.anl.gov/api/v1/compute/status/{resource_id}/{job_id}",
    params={"historical": "true"},
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 1.4. Cancel a Job

Cancels a queued or running job. Returns HTTP `204 No Content` on success.

```python
# Polaris
resource_id = "55c1c993-1124-47f9-b823-514ba3849a9a"
job_id = "<job_id>"

# Submit to IRI API
response = requests.delete(
    f"https://api.alcf.anl.gov/api/v1/compute/cancel/{resource_id}/{job_id}",
    headers=headers
)

print(response.status_code)
print("Job canceled." if response.status_code == 204 else response.json())
```

### 2. Filesystem

**Note**: All filesystem operations are asynchronous and will return a task ID. Please see the [Get a Task](#3-tasks) section for how to retrieve your results.

#### 2.1. List Directory Contents

Returns the contents of a directory on the specified resource.

```python
# Eagle
resource_id = "1c3ad9d4-2e91-42bc-becb-72b1fde1235c"

# Submit to IRI API
response = requests.get(
    f"https://api.alcf.anl.gov/api/v1/filesystem/ls/{resource_id}",
    params={"path": "/eagle/<your-project>"},
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 2.2. Create a Directory

Creates a new directory at the specified path. Set `parent` to `True` to create any missing parent directories.

```python
# Eagle
resource_id = "1c3ad9d4-2e91-42bc-becb-72b1fde1235c"

# Submit to IRI API
response = requests.post(
    f"https://api.alcf.anl.gov/api/v1/filesystem/mkdir/{resource_id}",
    json={
        "path": "/eagle/<your-project>/my_new_dir",
        "parent": False
    },
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 2.3. View File Contents

Returns a portion of a file starting at a given byte `offset` and reading up to `size` bytes.

```python
# Eagle
resource_id = "1c3ad9d4-2e91-42bc-becb-72b1fde1235c"

# Submit to IRI API
response = requests.get(
    f"https://api.alcf.anl.gov/api/v1/filesystem/view/{resource_id}",
    params={
        "path": "/eagle/<your-project>/file.txt",
        "size": 10,
        "offset": 0
    },
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 2.4. Read First Lines of a File

Returns the first N `lines` of a file, similar to the Unix `head` command.

```python
# Eagle
resource_id = "1c3ad9d4-2e91-42bc-becb-72b1fde1235c"

# Submit to IRI API
response = requests.get(
    f"https://api.alcf.anl.gov/api/v1/filesystem/head/{resource_id}",
    params={
        "path": "/eagle/<your-project>/file.txt",
        "lines": 3
    },
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 2.5. Change File Ownership

Changes the `owner` and/or `group` of a file or directory.

```python
# Eagle
resource_id = "1c3ad9d4-2e91-42bc-becb-72b1fde1235c"

# Submit to IRI API
response = requests.put(
    f"https://api.alcf.anl.gov/api/v1/filesystem/chown/{resource_id}",
    json={
        "path": "/eagle/<your-project>/file.txt",
        "owner": "<username>",
        "group": "<group>"
    },
    headers=headers
)

print(response.status_code)
print(response.json())
```

#### 2.6. Change File Permissions

Changes the permissions of a file or directory using an octal `mode` string.

```python
# Eagle
resource_id = "1c3ad9d4-2e91-42bc-becb-72b1fde1235c"

# Submit to IRI API
response = requests.put(
    f"https://api.alcf.anl.gov/api/v1/filesystem/chmod/{resource_id}",
    json={
        "path": "/eagle/<your-project>/file.txt",
        "mode": "700"
    },
    headers=headers
)

print(response.status_code)
print(response.json())
```

### 3. Tasks

#### 3.1. Get a Task

Retrieves the status and result of an asynchronous task by its ID.

```python
# Task ID returned by filesystem operations
task_id = "<task_id>"

response = requests.get(
    f"https://api.alcf.anl.gov/api/v1/task/{task_id}",
    headers=headers
)

print(response.status_code)
print(response.json())
```

## Troubleshooting

- **Permission Denied:** Your token may have expired or you may not be authenticated with your ALCF credentials. Logout from Globus at [app.globus.org/logout](https://app.globus.org/logout), clear your browser cache or use an incognito browser, and re-authenticate with `python alcf_facility_api_globus_token.py authenticate`.
- **IdentityMismatchError: Detected a change in identity:** This happens when trying to get an access token using a Globus identity that is not linked to the one you previously used to generate your access tokens. Locate your tokens file (typically at `~/.globus/app/8b84fc2d-49e9-49ea-b54d-b3a29a70cf31/alcf_facility_api_app/tokens.json`), delete it, and restart the authentication process.

## Internal Debugging

For those who own the appropriate Globus Client credentials, you can introspect your token with the `introspect_token.py` script. First, add your credentials in a `.env` file:

```bash
GLOBUS_SERVICE_API_CLIENT_ID=....
GLOBUS_SERVICE_API_CLIENT_SECRET=....
```

Then execute the introspection script to verify your token for any issues (e.g. `session_info`, `policy_evaluations`):

```bash
python introspect_token.py
```

## Contact Us

For questions or support, please contact [ALCF Support](mailto:support@alcf.anl.gov?subject=Facility%20API%20Token).
