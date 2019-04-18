from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.auth import app_engine
import config


def create_directory_service(user_email):
    """Build and returns an Admin SDK Directory service object authorized with the service accounts
    that act on behalf of the given user.

    Args:
      user_email: The email of the user. Needs permissions to access the Admin APIs.
    Returns:
      Admin SDK directory service object.
    """

    if config.USE_APP_ENGINE_SERVICE_ACCOUNT:
        credentials = app_engine.Credentials()
    else:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json",
            scopes=['https://www.googleapis.com/auth/admin.directory.group.member.readonly',
                'https://www.googleapis.com/auth/admin.directory.group.readonly'])

    credentials = credentials.create_delegated(user_email)

    return build('admin', 'directory_v1', credentials=credentials)

if config.ENABLE_GOOGLE_GROUPS_INTEGRATION:
    directory_service = create_directory_service(config.GSUITE_DIRECTORY_ADMIN_USER)
