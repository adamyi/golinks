from googleapiclient.discovery import build
#from google.auth import app_engine
from google.oauth2 import service_account
import config


def create_directory_service(user_email):
  """Build and returns an Admin SDK Directory service object authorized with the service accounts
    that act on behalf of the given user.

    Args:
      user_email: The email of the user. Needs permissions to access the Admin APIs.
    Returns:
      Admin SDK directory service object.
    """

  scopes = [
      'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
      'https://www.googleapis.com/auth/admin.directory.group.readonly'
  ]

  #if config.USE_APP_ENGINE_SERVICE_ACCOUNT:
  #  credentials = app_engine.Credentials()
  #else:
  sa_credentials = service_account.Credentials.from_service_account_file(
      "credentials.json", scopes=scopes)

  credentials = sa_credentials.with_subject(user_email)
  return build('admin', 'directory_v1', credentials=credentials)


if config.ENABLE_GOOGLE_GROUPS_INTEGRATION:
  directory_service = create_directory_service(
      config.GSUITE_DIRECTORY_ADMIN_USER)
