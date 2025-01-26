## Why?

Garmin can automatically sync activities from Stava, but:

1. There is no easy way to select which activities to sync, or when to sync
   them.
2. Garmin picks a boring title by default, which can only be changed by editing
   the activity in Stave after it has posted.

## Usage

Download latest activity from Garmin and upload it to Stava.

```
pixi run download
pixi run upload <filename> <title>
```

Verify success by viewing [Strava Activities](https://www.strava.com/athlete/training).

## Strava Auth, as explained by Claude and lightly edited by me

When setting up Strava API access, you need to explicitly request the `activity:write` scope. Let me help you update your authorization.

1. First, go to https://www.strava.com/settings/api and find your app's Client ID and Client Secret. **Or just look in strava_tokens.json.**

2. You'll need to re-authorize with the correct scope. Visit this URL in your browser (replace YOUR_CLIENT_ID):
```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:write,activity:read_all
```

3. After you authorize, you'll be redirected to localhost with a code parameter in the URL. Copy that code.

4. Within 10 seconds, use this code to get your refresh token. Run this cURL command (replace YOUR_CLIENT_ID, YOUR_CLIENT_SECRET, and YOUR_CODE):
```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d code=YOUR_CODE \
  -d grant_type=authorization_code
```

5. From the response, copy the `refresh_token` value

6. Update your strava_config.json with this new refresh token. The file should look like:
```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "refresh_token": "YOUR_NEW_REFRESH_TOKEN"
}
```

Now when you run the upload script, it should have the proper permissions to upload activities. Let me know if you need any clarification on these steps!
