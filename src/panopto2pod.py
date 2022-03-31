"""Panopto SOAP API usage Example."""
# mysql-connector-python
from mysql import connector
from panopto_api.PanoptoAPI import PanoptoSession
import logging
import requests
# import re

import utils

config = utils.read_config()

migration_DB_HOST = config['migration_DB']['host']
migration_DB_USER = config['migration_DB']['user']
migration_DB_PASS = config['migration_DB']['password']
migration_DB_NAME = config['migration_DB']['db_name']

host = config['Panopto']['host']
username = config['Panopto']['username']
password = config['Panopto']['password']

log = logging.getLogger("panopto2pod")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fileHandler = logging.FileHandler("log/panopto2pod.log", mode="a")
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
log.setLevel(logging.INFO)
log.addHandler(fileHandler)
log.addHandler(streamHandler)

GUID_TOPLEVEL = '00000000-0000-0000-0000-000000000000'


class panopto2pod():
    """Panopto to Pod migration class."""

    def __init__(self, server_url):
        """Instancie l'instance panopto2pod."""
        """Paramètres Panopto."""
        self.server_url = server_url

        """Instanciation des caches BDD."""
        self.folderBDD = {}
        self.sessionBDD = {}
        self.userBDD = {}

        """Connexion à la bdd de migration."""
        self.conn = connector.connect(
            host=migration_DB_HOST,
            user=migration_DB_USER,
            password=migration_DB_PASS,
            database=migration_DB_NAME,
        )
        self.myCursor = self.conn.cursor(dictionary=True)
        self.getBDD()

    def getBDD(self):
        """Get all ids from Panopto folder, session and user tables."""
        self.populate("panopto_folder", 'nb_child', self.folderBDD)
        self.populate("panopto_session", 'MP4Url', self.sessionBDD)
        self.populate("auth_user", 'panopto_id', self.userBDD)

    def populate(self, table, col, dico):
        """Store a list of all ids from a DB table in a local dict."""
        requete = "SELECT * FROM %s" % table
        self.myCursor.execute(requete)
        data = self.myCursor.fetchall()
        for item in data:
            dico[item['id']] = item[col]
        return data

    def insertFolderBDD(self, folder, parent_id):
        """Insert a new folder in database."""
        if folder['Id'] not in self.folderBDD.keys():
            requete = """
                      INSERT INTO panopto_folder (id, name, parent)
                      VALUES (%s, %s, %s)
                      """
            self.myCursor.execute(requete,
                                  (folder['Id'], folder['Name'], parent_id))
            self.conn.commit()
            print(self.myCursor.rowcount, " record inserted.")
            self.folderBDD[folder['Id']] = None
            log.info("# nb folders dans BDD : %s " % (len(self.folderBDD)))

    def insertUserBDD(self, user):
        """Insert a new user in database."""
        if user['UserId'] not in self.userBDD.values():
            requete = """
                      INSERT INTO auth_user (first_name, last_name,
                      email, panopto_name, panopto_id)
                      VALUES (%s, %s, %s, %s, %s)
                      """
            data = (user['FirstName'], user['LastName'], user['Email'],
                    user['UserKey'], user['UserId'])
            self.myCursor.execute(requete, data)
            self.conn.commit()
            print(self.myCursor.rowcount, " record inserted.")
            self.userBDD[len(self.userBDD)] = user['UserId']

    def updateFolderBDD(self, folderId, nbChild):
        """Update amount of children of a folder in database."""
        requete = """
                  UPDATE panopto_folder
                  SET nb_child = %s
                  WHERE Id = %s
                  """
        self.myCursor.execute(requete, (nbChild, folderId))
        self.conn.commit()
        log.info("%s panopto_folder updated." % self.myCursor.rowcount)

    def updateSessionBDD(self, sessionId, value, field="filesize"):
        """Update one field of a session in database."""
        requete = """
                  UPDATE panopto_session
                  SET {field} = %s
                  WHERE Id = %s
                  """.format(field=field)
        self.myCursor.execute(requete, (value, sessionId))
        self.conn.commit()
        log.info("panopto_session %s updated (%s=%s)." % (sessionId, field, value))

    def updateFieldsSessionBDD(self, sessionId, values, fields):
        """Update multiple fields of a session in database."""
        mset = " = %s,".join(fields)
        requete = """
                  UPDATE panopto_session
                  SET {mset} = %s
                  WHERE Id = '{id}'
                  """.format(mset=mset, id=sessionId)

        self.myCursor.execute(requete, values)
        self.conn.commit()
        log.info("%s panopto_session updated." % self.myCursor.rowcount)

    def insertFoldersBDD(self, folders, parent_id):
        """Insert multiple new folders in database."""
        data = []
        for folder in folders:
            if folder['Id'] not in self.folderBDD.keys():
                data.append((folder['Id'], folder['Name'], parent_id))
                self.folderBDD[folder['Id']] = None

        requete = """
                  INSERT INTO panopto_folder (id, name, parent)
                  VALUES (%s, %s, %s)
                  """
        self.myCursor.executemany(requete, data)
        self.conn.commit()
        log.info("%s panopto_folder inserted." % self.myCursor.rowcount)

    def insertSessionsBDD(self, sessions):
        """Insert multiple new sessions in database."""
        data = []
        newIds = []
        updated = 0
        updateFields = ["MP4Url", "State", "StatusMessage", "IsBroadcast",
                        "IsDownloadable", "CreatorId"]
        for sess in sessions:
            if sess['Id'] not in self.sessionBDD.keys():
                data.append((sess['Id'], sess['Name'], sess['Description'],
                             sess['FolderId'], sess['StartTime'], sess['Duration'],
                             sess['CreatorId'], sess["MP4Url"], sess["State"],
                             sess["StatusMessage"], sess["IsBroadcast"],
                             sess["IsDownloadable"]))
                self.sessionBDD[sess['Id']] = sess['MP4Url']
                newIds.append(sess['Id'])
            else:
                updated += 1
                values = (sess["MP4Url"], sess["State"],
                          sess["StatusMessage"], sess["IsBroadcast"],
                          sess["IsDownloadable"], sess["CreatorId"])
                self.updateFieldsSessionBDD(sess['Id'], values, updateFields)

        print("%s sessions updated in DB." % updated)
        print("Inserting %s new sessions in DB." % len(data))
        requete = """
                  INSERT INTO panopto_session
                  (id, Name, Description, Folder, StartTime, Duration,
                   CreatorId, MP4Url, State, StatusMessage,
                   IsBroadcast, IsDownloadable)

                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  ON DUPLICATE KEY
                      UPDATE
                      State = VALUES(State),
                      StatusMessage = VALUES(StatusMessage),
                      Description = VALUES(Description),
                      Name = VALUES(Name)
                  """
        self.myCursor.executemany(requete, data)
        self.conn.commit()
        return newIds

    def updateMissingPodcastSize(self):
        """Update missing sizes of all podcasts in BDD."""
        requete = """SELECT *
                     FROM panopto_session
                     WHERE state='Complete'
                     AND filesize IS NULL
                  """
        self.myCursor.execute(requete)
        podcasts = self.myCursor.fetchall()
        log.info("%s podcasts missing file size in DB" % len(podcasts))
        for pod in podcasts:
            self.updatePodcastSize(pod['id'])

    def updatePodcastSize(self, sessionId):
        """Update Podcast size in BDD."""
        url = self.sessionBDD[sessionId]
        file_size = -1
        if url:
            resp = requests.get(url=url, stream=True)
            try:
                file_size = resp.headers['Content-Length']
            except KeyError:
                if resp.status_code == 403:
                    print("%s - Download forbidden." % sessionId)
                    self.updateSessionBDD(sessionId, False, "PublicDownload")
                else:
                    print("No content length for: %s" % sessionId)
                    print("Status: %s" % resp.status_code)
            self.updateSessionBDD(sessionId, file_size)
        return file_size

    def updateCreators(self):
        """Update missing creators in DB."""
        requete = """SELECT DISTINCT CreatorId
                     FROM panopto_session
                     WHERE CreatorId NOT IN
                     (SELECT panopto_id FROM auth_user)
                  """
        self.myCursor.execute(requete)
        creators = self.myCursor.fetchall()
        log.info("%s missing creators in DB" % len(creators))

        for creator in creators:
            # Certaines sessions n'ont pas de createur.
            if creator["CreatorId"]:
                for u in panopto.getUsers(creator["CreatorId"]):
                    self.insertUserBDD(u)

    def updateUserNames(self):
        """Update missing usernames in DB."""
        requete = """SELECT * FROM auth_user
                     WHERE username = ''
                  """
        self.myCursor.execute(requete)
        users = self.myCursor.fetchall()
        print("%s missing usernames" % len(users))
        for user in users:
            username = user['panopto_name'].split('\\')[-1]
            requete = """
                  UPDATE auth_user
                  SET username = %s
                  WHERE Id = %s
                  """
            self.myCursor.execute(requete, (username, user['id']))
        self.conn.commit()

    def updateUserIds(self):
        """Update user ids from Pod."""
        requete = "SELECT * FROM auth_user WHERE is_active = 0"
        self.myCursor.execute(requete)
        my_users = self.myCursor.fetchall()

        n = 0
        e = 0

        connPod = connector.connect(
            host=migration_DB_HOST,
            user=migration_DB_USER,
            password=migration_DB_PASS,
            database='pod',
        )
        cursorPod = connPod.cursor(dictionary=True)
        # On ne prend que les comptes sans doublon
        requetePod = """SELECT * FROM auth_user
                        WHERE main_id IS NULL
                        AND email = '%s'"""
        for user in my_users:
            if user['email'] != '':
                print("%s" % user['email'])
                cursorPod.execute(requetePod % user['email'])
                pod_user = cursorPod.fetchone()
                if pod_user:
                    requete = """UPDATE auth_user
                                 SET id = %s,
                                 is_active = 1
                                 WHERE panopto_id = %s
                              """

                    self.myCursor.execute(requete, (pod_user['id'], user['panopto_id']))
                    n += 1

        print("%s updateUserIds DONE. (%s errors)" % (n, e))
        self.conn.commit()

    def correctDoublons(self):
        """Corrige les utilisateurs en doublons dans la BDD."""
        req = """SELECT COUNT(username) AS nbr_doublon, username
              FROM     auth_user
              GROUP BY username
              HAVING   COUNT(username) > 1"""
        self.myCursor.execute(req)
        doublons = self.myCursor.fetchall()

        for d in doublons:
            # On cherche l'utilisateur actif ayant cet username.
            req = """SELECT id FROM auth_user
                WHERE is_active = 1 AND username = %s"""
            self.myCursor.execute(req, [d['username']])
            main_user = self.myCursor.fetchone()
            if main_user:
                # On indique son id dans le champ 'main_id' des doublons
                req = """UPDATE auth_user
                  SET main_id = %s
                  WHERE is_active = 0 AND username = %s"""
                self.myCursor.execute(req, (main_user['id'], d['username']))
            else:
                print("aucun user principal trouvé pour %s" % d['username'])
        self.conn.commit()

    def InsertOrUpdatePods(self):
        """Insert pods from Panopto session (update if exists)."""
        requete = "SELECT * FROM panopto_session WHERE State='Complete'"
        self.myCursor.execute(requete)
        sessions = self.myCursor.fetchall()

        requete = "SELECT * FROM auth_user"
        self.myCursor.execute(requete)
        users = self.myCursor.fetchall()

        # On crée un dico des users en tenant compte des doublons
        inv_users = {}
        for u in users:
            if u['main_id']:
                inv_users[u['panopto_id']] = u['main_id']
            else:
                inv_users[u['panopto_id']] = u['id']

        data = []
        for sess in sessions:

            owner_id = inv_users[sess['CreatorId']]
            if sess['Description']:
                desc = sess['Description']
            else:
                desc = ""
            # if sess['id'] == '0b40341c-d33e-4549-ba23-ae4c00b4b7db':
            log.debug("SESSION = %s (%s)" % (sess['id'], owner_id))
            data = (sess['id'], sess['Name'],
                    desc, sess['StartTime'],
                    sess['StartTime'],
                    sess['Duration'], owner_id,
                    sess['MP4Url'])
            requete = """
                      INSERT INTO pods_pod
                      (panopto_session, title, description,
                       date_added, date_evt, duration, owner_id,
                       video, type_id)
                      VALUES (%s, %s, %s,
                       %s, %s, %s, %s, %s, 1)
                      ON DUPLICATE KEY
                      UPDATE
                      panopto_session = VALUES(panopto_session),
                      title = VALUES(title),
                      description = VALUES(description),
                      date_added = VALUES(date_added),
                      date_evt = VALUES(date_evt),
                      duration = VALUES(duration),
                      owner_id = VALUES(owner_id),
                      video = VALUES(video)
                      """
            self.myCursor.execute(requete, data)
        self.conn.commit()
        log.info("%s pods_pod updated." % self.myCursor.rowcount)


##############
# Pré-requis :
# * disposer des bonnes configs dans le fichier /config/settings.ini

panopto2pod = panopto2pod(host)
panopto = PanoptoSession(host, username, password)

sessions = panopto.getSessionsList()

newIds = panopto2pod.insertSessionsBDD(sessions)
log.info("Total: %s sessions." % len(sessions))

""" Update missing sizes in sessionBDD. """
n = 1
for sess in newIds:
    # Check if we have any MP4Url
    if panopto2pod.sessionBDD[sess]:
        size = panopto2pod.updatePodcastSize(sess)
        print("%s/%s -- File size: %s" % (n, len(newIds), size))
        n += 1


"""Insert Missing creators."""
panopto2pod.updateCreators()
"""Insert/Update pods from Panopto session (update if exists)."""
panopto2pod.InsertOrUpdatePods()

