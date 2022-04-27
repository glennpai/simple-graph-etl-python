"""
Module to simplify basic Python ETL interactions with a SharePoint document library
"""
import os
import re
import msal
import requests

class SimpleETL:
    """
    A class to simplify ETL functions perfomed on Azure app registrations and SharePoint
    document libraries via the Graph API

    Class constructor accepts a DocumentLibrary instance and the required authentication
    configuration

    Attributes:
        library (DocumentLibrary): SharePoint document library configuration
        __thumbprint [private] (string): Hash of signed certificate used when authenticating to the
            Azure app registration
        __private_key [private] (string): Private key used to authenticate to the Azure app
            registration
        __token [private] (string): Authentication token acquired from Azure app registration
    """
    def __init__(self, document_library, thumbprint, private_key):
        self.library = document_library
        self.__thumbprint = thumbprint
        self.__private_key = private_key
        self.__token = self.__acquire_token()


    @staticmethod
    def __get_item_id(file_items, target_name):
        """
        Gets item ID value from a file object if its name matches the target name

        Parameters:
            file_items (any[]): List of file objects to check
            target_name (string): Name to search for in list of file objects
        Returns:
            item_id (string): Item ID property value
        """
        item_id = ''

        for item in file_items:
            if item['name'] == target_name:
                item_id = item['id']

        return item_id


    def __acquire_token(self):
        """
        Authenticates against Azure app registration to get an auth token used for
        calls to the Graph API

        Parameters:
        Returns:
            result['access_token'] (string): String value of auth token
        """
        app = msal.ConfidentialClientApplication(
            self.library.client_id,
            authority=self.library.authority,
            client_credential={'thumbprint': self.__thumbprint, 'private_key': self.__private_key},
        )
        result = None
        result = app.acquire_token_silent([self.library.scope], account=None)

        if not result:
            result = app.acquire_token_for_client(scopes=[self.library.scope])
        if 'access_token' in result:
            return result['access_token']

        raise Exception(result.get('error'))


    def filenames(self, remote_path):
        """
        Gets a list of file names that are children to the remote_path directory
        Useful for checking existence of a remote file

        Parameters:
            remote_path (string): Path to parent directory containing target files
        Returns:
            filenames (string[]): List of file names in the remote_path directory
        """
        filenames = []
        file_list_resp = requests.get(f'{self.library.base_url}/root:/{remote_path}:/children',
                                headers={'Authorization': 'Bearer ' + self.__token})

        if file_list_resp.status_code == 200:
            objs = file_list_resp.json()['value']
            for obj in objs:
                if obj['file']:
                    filenames.append(obj['name'])
        else:
            raise Exception('Bad response from the remote host.' +
                f'{file_list_resp.raise_for_status()}')

        return filenames


    def fetch(self, remote_path, local_path='.'):
        """
        Creates a local copy of files contained in the document library at the remote_path

        Parameters:
            remote_path (string): Path to parent directory containing target files
            local_path (string): Path to local directory where files will be written - Default '.'
        Returns:
        """
        file_list_resp = requests.get(f'{self.library.base_url}/root:/{remote_path}:/children',
                                headers={'Authorization': 'Bearer ' + self.__token})
        if file_list_resp.status_code == 200:
            objs = file_list_resp.json()['value']
            for obj in objs:
                if not obj['file']:
                    continue
                file_data = requests.get(obj['@microsoft.graph.downloadUrl'])
                if file_data.status_code == 200:
                    try:
                        clean_path = re.sub(r'^(\\|\/)+|(\\|\/)+$', '', local_path)
                        if not os.path.exists(clean_path):
                            os.makedirs(clean_path)
                        with open(os.path.join(clean_path, obj['name']), 'wb') as file:
                            file.write(file_data.content)
                    except Exception as err:
                        raise f'Failed to write file data. {err}'
                else:
                    raise Exception(f'Bad response fetching file "{obj["name"]}".' +
                        f'{file_data.raise_for_status()}')
        else:
            raise Exception('Bad response from the remote host.' +
                f'{file_list_resp.raise_for_status()}')


    def delete(self, remote_path, file_name):
        """
        Deletes a remote file from a SharePoint document library based on file path
        and name

        Parameters:
            remote_path (string): Remote path of parent directory of file to delete
            file_name (string): Name of remote file to delete
        Returns:
        """
        list_url = f'{self.library.base_url}/root:/{remote_path}:/children'
        file_list_response = requests.get(list_url,
            headers={'Authorization': 'Bearer ' + self.__token})

        if file_list_response.status_code == 200:
            item_id = self.__get_item_id(file_list_response.json()['value'], file_name)
            if item_id != '':
                delete_url = f'{self.library.base_url}/items/'
                delete_response = requests.delete(delete_url + item_id,
                    headers={'Authorization': 'Bearer ' + self.__token})
                if delete_response.status_code != 204:
                    raise Exception(f'Failed to delete {file_name}. \
                        {delete_response.raise_for_status()}')
            else:
                raise Exception(f'Failed to fetch item info for {file_name}')
        else:
            raise Exception(f'Failed to fetch file list from {remote_path}. \
                {file_list_response.raise_for_status()}')


    def upload(self, file_name, remote_path, local_path='.'):
        """
        Uploads a local file to a SharePoint document library at a specified remote_path

        Parameters:
            local_file (string): Local file name and format
            remote_path (string): Remote path of parent directory of file to upload
            local_path (string): Local path to file - Default '.'
        Returns:
        """
        upload_session = requests.post(f'{self.library.base_url}/root:/ \
            {remote_path}/{file_name}:/createUploadSession',
            headers={'Authorization': 'Bearer ' + self.__token})

        if upload_session.status_code == 200:
            upload_url = upload_session.json()['uploadUrl']
            try:
                full_local = os.path.join(local_path, file_name)
                with open(full_local, 'rb') as file:
                    file_size = os.path.getsize(full_local)
                    # Content length and content range are required headers.
                    # File data (bytes) is sent in body.
                    upload_response = requests.put(upload_url,
                        headers={'Content-Length': f'{file_size}',
                        'Content-Range': f'bytes 0-{file_size - 1}/{file_size}'},
                        data=file)
                    if upload_response.status_code != 201:
                        raise Exception(upload_response.raise_for_status())
            except Exception as err:
                raise f'Failed to upload file to upload URL. {err}'
        else:
            raise Exception(f'Error retrieving upload URL. {upload_session.raise_for_status()}')
