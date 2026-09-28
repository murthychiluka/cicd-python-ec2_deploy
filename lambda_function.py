import json
import boto3
import urllib.request
import os


secrets_manager = boto3.client("secretsmanager")

SECRET_NAME = "github/actions-token"

GITHUB_OWNER = "murthychiluka"
GITHUB_REPO = "cicd-python-ec2_deploy"
WORKFLOW_FILE = "deploy.yml"
BRANCH = "main"


def lambda_handler(event, context):

    # Get GitHub token from Secrets Manager
    response = secrets_manager.get_secret_value(
        SecretId=SECRET_NAME
    )

    secret = json.loads(response["SecretString"])
    github_token = secret["token"]

    # GitHub API URL
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}/"
        f"actions/workflows/{WORKFLOW_FILE}/dispatches"
    )

    # Workflow dispatch payload
    payload = {
        "ref": BRANCH
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    request.add_header(
        "Authorization",
        f"Bearer {github_token}"
    )

    request.add_header(
        "Accept",
        "application/vnd.github+json"
    )

    request.add_header(
        "X-GitHub-Api-Version",
        "2022-11-28"
    )

    try:

        with urllib.request.urlopen(request) as response:

            print(
                f"GitHub workflow triggered. "
                f"HTTP status: {response.status}"
            )

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "GitHub Actions workflow triggered successfully"
                })
            }

    except Exception as e:

        print(f"Error triggering GitHub Actions: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to trigger GitHub Actions",
                "error": str(e)
            })
        }
