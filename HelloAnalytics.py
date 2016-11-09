#-*- coding: utf-8 -*-

import argparse
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools



def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  credentials = ServiceAccountCredentials.from_p12_keyfile(
    service_account_email, key_file_location, scopes=scope)

  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service


def get_first_profile_id(service):
  # Use the Analytics service object to get the first profile id.

  #Получаем список аккаунтов пользователя
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    #Берем первый попавшийся аккаунт гугл-аналитикс
    account = accounts.get('items')[0].get('id')

    #Получаем список всех параметров аккаунта
    properties = service.management().webproperties().list(
        accountId=account).execute()

    if properties.get('items'):
      #Получаем идентификатор первого параметра
      property = properties.get('items')[0].get('id')

      # Get a list of all views (profiles) for the first property.
      profiles = service.management().profiles().list(
          accountId=account,
          webPropertyId=property).execute()

      if profiles.get('items'):
        # return the first view (profile) id.
        return profiles.get('items')[0].get('id')

  return None


def get_results(service, profile_id, past):

  #Используем объект Analytics Service, чтобы выполнить запрос к Core Reporting API
  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date= str(past) + 'daysAgo',
      end_date='today',
      metrics='ga:uniqueEvents',
      dimensions='ga:eventAction, ga:eventCategory',
      filters='ga:eventCategory==watches'
      ).execute()


def print_results(results):
  # Print data nicely for the user.
  if results:
    print 'View (Profile): %s' % results.get('profileInfo').get('profileName')
    print 'Total Sessions: %s' % results.get('rows')[0][0]

  else:
    print 'No results found'


def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']

  # Use the developer console and replace the values with your
  # service account email and relative location of your key file.
  service_account_email = 'pythonanalytics@kinetic-magnet-149012.iam.gserviceaccount.com'
  key_file_location = 'client_secrets.p12'

  # Authenticate and construct service.
  service = get_service('analytics', 'v3', scope, key_file_location,
    service_account_email)
  profile = get_first_profile_id(service)

  print profile

  for i in range(10):
    print_results(get_results(service, profile, i))


if __name__ == '__main__':
  main()
