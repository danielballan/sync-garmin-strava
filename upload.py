import requests
import time
import sys
import json
import os
from datetime import datetime

class StravaUploader:
    def __init__(self):
        self.auth_url = "https://www.strava.com/oauth/token"
        self.upload_url = "https://www.strava.com/api/v3/uploads"
        
        # Load credentials from config file
        self.load_config()

    def load_config(self):
        """Load Strava credentials from config file"""
        try:
            if os.path.exists('strava_config.json'):
                with open('strava_config.json', 'r') as f:
                    config = json.load(f)
                    self.client_id = config.get('client_id')
                    self.client_secret = config.get('client_secret')
                    self.refresh_token = config.get('refresh_token')
            else:
                self.setup_initial_config()
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            sys.exit(1)

    def setup_initial_config(self):
        """Set up initial configuration with user input"""
        print("\nFirst-time setup: Please enter your Strava API credentials")
        print("You can get these from https://www.strava.com/settings/api")
        
        self.client_id = input("Enter your Client ID: ")
        self.client_secret = input("Enter your Client Secret: ")
        self.refresh_token = input("Enter your Refresh Token: ")
        
        # Save the config
        config = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }
        
        with open('strava_config.json', 'w') as f:
            json.dump(config, f)

    def get_access_token(self):
        """Get a new access token using the refresh token"""
        try:
            response = requests.post(
                self.auth_url,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token
                }
            )
            response.raise_for_status()
            return response.json()['access_token']
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            sys.exit(1)

    def upload_activity(self, file_path, activity_type=None, name=None, description=None):
        """Upload an activity file to Strava"""
        try:
            # Get access token
            access_token = self.get_access_token()
            
            # Prepare the upload data
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    'data_type': file_path.split('.')[-1].lower(),  # tcx, gpx, or fit
                }
                
                if activity_type:
                    data['activity_type'] = activity_type
                if name:
                    data['name'] = name
                if description:
                    data['description'] = description

                # Start the upload
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.post(
                    self.upload_url,
                    files=files,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                upload_id = response.json().get('id')
                
                # Check upload status
                return self.check_upload_status(upload_id, access_token)
                
        except Exception as e:
            print(f"Error uploading activity: {str(e)}")
            sys.exit(1)

    def check_upload_status(self, upload_id, access_token, max_checks=30, check_interval=2):
        """Check the status of an upload"""
        status_url = f"{self.upload_url}/{upload_id}"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        for _ in range(max_checks):
            try:
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                status = response.json()
                
                if status.get('error'):
                    raise Exception(status['error'])
                
                if status.get('activity_id'):
                    return status['activity_id']
                    
                if status.get('status') == 'processing':
                    time.sleep(check_interval)
                    continue
                    
            except Exception as e:
                print(f"Error checking upload status: {str(e)}")
                sys.exit(1)
                
        raise Exception("Upload timed out")

def main():
    if len(sys.argv) < 2:
        print("Usage: python strava_upload.py <activity_file> [activity_name] [activity_type] [description]")
        sys.exit(1)

    file_path = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else None
    activity_type = sys.argv[3] if len(sys.argv) > 3 else None
    description = sys.argv[4] if len(sys.argv) > 4 else None

    uploader = StravaUploader()
    activity_id = uploader.upload_activity(file_path, activity_type, name, description)
    
    print(f"\nUpload successful!")
    print(f"View your activity at: https://www.strava.com/activities/{activity_id}")

if __name__ == "__main__":
    main()
