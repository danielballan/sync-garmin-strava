import json
import logging
import os
import sys
from datetime import datetime

import garth
from dotenv import load_dotenv
from garth.exc import GarthHTTPError
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

# Load environment variables from .env file
load_dotenv()
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"


def get_credentials():
    """Get Garmin credentials from user input"""
    return os.environ["EMAIL"], os.environ["PASSWORD"]


def initialize_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        # Using Oauth1 and Oauth2 tokens from base64 encoded string
        # print(
        #     f"Trying to login to Garmin Connect using token data from file '{tokenstore_base64}'...\n"
        # )
        # dir_path = os.path.expanduser(tokenstore_base64)
        # with open(dir_path, "r") as token_file:
        #     tokenstore = token_file.read()

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
            if not email or not password:
                email, password = get_credentials()

            garmin = Garmin(
                email=email, password=password, is_cn=False, prompt_mfa=get_mfa
            )
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            print(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)\n"
            )
            # Encode Oauth1 and Oauth2 tokens to base64 string and safe to file for next login (alternative way)
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            print(
                f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)\n"
            )
        except (
            FileNotFoundError,
            GarthHTTPError,
            GarminConnectAuthenticationError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error(err)
            return None

    return garmin


def get_mfa():
    """Get MFA."""

    return input("MFA one-time code: ")


def get_latest_activity(client):
    """Get the most recent activity"""
    try:
        # Get activities from the API
        activities = client.connectapi(
            path="/activitylist-service/activities/search/activities",
            params={"limit": 1, "start": 0}
        )

        if not activities:
            print("No activities found.")
            sys.exit(1)
        return activities[0]
    except Exception as e:
        print(f"Error getting activities: {str(e)}")
        sys.exit(1)

def download_activity(client, activity_id):
    """Download activity in specified format"""
    try:
        data = client.download_activity(
            activity_id, dl_fmt=client.ActivityDownloadFormat.TCX
        )
        filename = f"activity_{activity_id}.tcx"
        with open(filename, 'wb') as f:
            f.write(data)
        return filename
    except Exception as e:
        print(f"Error downloading activity: {str(e)}")
        sys.exit(1)

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Get credentials and initialize API
    email, password = get_credentials()
    client = initialize_api(email, password)

    # Get the most recent activity
    activity = get_latest_activity(client)
    activity_id = activity["activityId"]
    activity_name = activity["activityName"]
    activity_date = datetime.fromisoformat(activity["startTimeLocal"].replace('Z', '+00:00'))

    print(f"\nLatest activity found:")
    print(f"Name: {activity_name}")
    print(f"Date: {activity_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"Activity ID: {activity_id}")

    # Download in TCX format (most compatible with Strava)
    filename = download_activity(client, activity_id)
    print(f"\nActivity downloaded successfully as {filename}")
    print("You can now upload this file to Strava.")

if __name__ == "__main__":
    main()
