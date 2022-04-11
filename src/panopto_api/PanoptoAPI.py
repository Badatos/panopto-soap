"""Panopto SOAP API."""

from panopto_api.AuthenticatedClientFactory import AuthenticatedClientFactory


class PanoptoSession:
    """Panopto SOAP API."""

    def __init__(self, host, username, password):
        """Initialize."""
        # create a client factory for making authenticated API requests
        self.auth = AuthenticatedClientFactory(
            host=host, username=username,
            password=password, verify_ssl=host != "localhost"
        )

        self.sessions = self.auth.get_client("SessionManagement")
        self.users = self.auth.get_client("UserManagement")

    def updateFolderEnablePodcast(self, guid, enablePodcast=True):
        """
        Update the enable podcast bit on a folder.

        Must be called by a creator or admin.
        """
        response = self.sessions.call_service(
            "UpdateFolderEnablePodcast", Guid=guid, enablePodcast=enablePodcast
        )
        return response

    def getFoldersList(self, request=None, searchQuery=None):
        """
        Update the enable podcast bit on a folder.

        Must be called by a creator or admin.
        @see https://support.panopto.com/resource/APIDocumentation/Help/html/93a3f1b2-d5f2-0d2e-25f4-43aebd25109f.htm
        """
        if not request:
            request = {"Pagination": {"MaxNumberResults": 25, "PageNumber": 0}}
        response = self.sessions.call_service(
            "GetFoldersList", request=request, searchQuery=searchQuery
        )
        return response

    def getSessionsList(self, searchQuery=None):
        """
        List all the sessions the user has access to.

        Filtered, sorted, and paginated by the parameters in ListSessionsRequest.
        Note, the RemoteRecorderId filter only applies to a session's primary remote recorder.
        @see https://support.panopto.com/resource/APIDocumentation/Help/html/e9134a1f-39ef-5f78-b1a3-cc425830664c.htm
        """
        pageNumber = 0
        maxResults = 1000
        nbSessions = maxResults
        sessList = []

        request = {
            "Pagination": {"MaxNumberResults": maxResults, "PageNumber": pageNumber}
        }
        while nbSessions >= maxResults:
            print("Get Session list (page %s)" % pageNumber)
            request["Pagination"]["PageNumber"] = pageNumber
            response = self.sessions.call_service(
                "GetSessionsList", request=request, searchQuery=searchQuery
            )
            if response["Results"]:
                sess = response["Results"]["Session"]
                nbSessions = len(sess)
                sessList += sess
                pageNumber += 1
            else:
                print("0 SESSION FOUND. %s" % response)
                print("REQUEST: %s" % request)
                break
        return sessList

    """
        Users
    """

    def listUsers(self, match_pattern=""):
        """
        Get users.

        Can be used to sort, search, and paginate the results.
        Can only be called by an admin
        """
        return self.users.call_service(
            "ListUsers", searchQuery=match_pattern, parameters={}
        )

    def getUsers(self, userIds):
        """
        Get information about multiple users by ID.

        Can only be called by an admin
        """
        return self.users.call_service("GetUsers", userIds=userIds)
