"""
Module to unify and simplify configuration of a SharePoint document library for use in
a Python ETL
"""
class DocumentLibrary:
    """
    A class containing configuration for accessing a SharePoint document library
        via the Graph API

    Attributes:
        client_id (string): Client ID for Azure Active Directory subscription
        site_id (string): Site ID for a library's parent SharePoint site
        res_id (string): Resource ID of a SharePoint document library
        authority (string): Authority string for an Azure app registration
        scope (string): Permission scopes of the user authenticating to the Azure app registration
        base_url (string): Base URL of the document library formed from the Site and Res IDs
    """
    # Pylint(R0913:too-many-arguments)
    # Ignoring in interest of keeping config flat and consistent
    def __init__(self, client_id, site_id, res_id, authority, scope):
        self.client_id = client_id
        self.site_id = site_id
        self.res_id = res_id
        self.authority = authority
        self.scope = scope
        self.base_url = self.get_base_url()


    def __repr__(self):
        return f'DocumentLibrary({self.client_id},{self.site_id},{self.res_id}, \
            {self.authority},{self.scope},{self.base_url}'


    def get_base_url(self):
        """
        Returns base URL used in most ETL functions via the Graph API

        Parameters:
        Returns:
            URL string constructed from site and res IDs
        """
        return f'https://graph.microsoft.com/v1.0/sites/ \
            {self.site_id}/drives/{self.res_id}'
