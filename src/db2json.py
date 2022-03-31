# -*- coding: utf-8 -*-
"""Export migration DB to JSON."""

# mysql-connector-python
from mysql import connector
import logging
import utils
import json

config = utils.read_config()

migration_DB_HOST = config["migration_DB"]["host"]
migration_DB_USER = config["migration_DB"]["user"]
migration_DB_PASS = config["migration_DB"]["password"]
migration_DB_NAME = config["migration_DB"]["db_name"]


pod_DB_HOST = config["pod_DB"]["host"]
pod_DB_PORT = config["pod_DB"]["port"]
pod_DB_USER = config["pod_DB"]["user"]
pod_DB_PASS = config["pod_DB"]["password"]
pod_DB_NAME = config["pod_DB"]["db_name"]

log = logging.getLogger("export_to_json")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fileHandler = logging.FileHandler("export_to_json.log", mode="a")
fileHandler.setFormatter(formatter)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
log.setLevel(logging.DEBUG)
log.addHandler(fileHandler)
log.addHandler(streamHandler)


class export2json:
    """export2json migration class."""

    def __init__(self):
        """Instancie l'instance export2json."""
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
        self.populate("panopto_folder", "nb_child", self.folderBDD)
        self.populate("panopto_session", "MP4Url", self.sessionBDD)
        self.populate("auth_user", "panopto_id", self.userBDD)

    def populate(self, table, col, dico):
        """Store a list of all ids from a DB table in a local dict."""
        requete = "SELECT * FROM %s" % table
        self.myCursor.execute(requete)
        data = self.myCursor.fetchall()
        for item in data:
            dico[item["id"]] = item[col]
        return data

    def user2json(self, user):
        """Convert an auth_user db entry to json."""
        if user["last_name"] is not None:
            return {
                "model": "auth.user",
                "fields": {
                    "is_superuser": False,
                    "username": user["username"].replace("@unice.fr", ""),
                    "first_name": user["first_name"],
                    "last_name": user["last_name"].capitalize(),
                    "email": user["email"],
                    "is_staff": False,
                    "is_active": True,
                },
            }
        else:
            print("ERROR. USER %s has no LASTNAME." % user["username"])

    def getInactiveUsers(self):
        """List all users which id is not synchro with Pod."""
        # Cherche tous les utilisateurs qui ne sont pas encore dans Pod,
        # en évitant les doublons
        req = """SELECT * FROM auth_user
                WHERE is_active = 0
                AND main_id IS NULL
                ORDER BY username"""
        self.myCursor.execute(req)
        return self.myCursor.fetchall()

    def exportUsers(self):
        """Export missing users to a json file."""
        users = []
        data = self.getInactiveUsers()
        for user in data:
            users.append(self.user2json(user))
        with open("sample_json/Users.json", "w") as json_file:
            json.dump(users, json_file)

    def synchroPodUsers(self):
        """Synchronise les id utilisateurs de la base locale avec ceux de Pod."""
        # Connexion à la bdd de migration.
        connPod = connector.connect(
            host=pod_DB_HOST,
            port=pod_DB_PORT,
            user=pod_DB_USER,
            password=pod_DB_PASS,
            database=pod_DB_NAME,
        )
        cursorPod = connPod.cursor(dictionary=True)

        dataLoc = self.getInactiveUsers()
        for user in dataLoc:
            req = """SELECT id, is_active FROM auth_user WHERE username = %s"""
            cursorPod.execute(req, [user["username"]])
            dataPod = cursorPod.fetchone()
            if dataPod is not None:
                requete = """
                  UPDATE auth_user
                  SET id = %s,
                  is_active = %s
                  WHERE id = %s
                  """
                self.myCursor.execute(
                    requete, (dataPod["id"], dataPod["is_active"], user["id"])
                )
                log.debug("%s record updated." % self.myCursor.rowcount)
        self.conn.commit()

    def getSelectedPods(self):
        """List all pods selected for migration."""
        req = """SELECT * FROM pods_pod p
                INNER JOIN migration m
                ON p.id = m.pod_id
                WHERE m.state = 10
                """
        self.myCursor.execute(req)
        return self.myCursor.fetchall()

    def pod2json(self, pod):
        """Convert a pods_pod db entry to json."""
        is_draft = False
        is_restricted = False
        if pod["access_type"] == "private":
            is_draft = True
        if pod["access_type"] == "restricted":
            is_restricted = True

        return {
            "model": "video.video",
            "fields": {
                "video": pod["video"],
                "allow_downloading": pod["allow_downloading"],
                "title": pod["title"],
                "owner": pod["owner_id"],
                "date_added": pod["date_added"].strftime("%Y-%m-%d"),
                "date_evt": pod["date_evt"].strftime("%Y-%m-%d"),
                "cursus": "0",
                "main_lang": "fr",
                "description": pod["description"],
                "duration": pod["duration"],
                "type": pod["type_id"],
                "is_draft": is_draft,
                "is_restricted": is_restricted,
                "password": pod["id"],
            },
        }

    def exportPods(self):
        """Export missing users to json."""
        pods = []
        data = self.getSelectedPods()
        for user in data:
            pods.append(self.pod2json(user))
        with open("sample_json/Pods.json", "w") as json_file:
            json.dump(pods, json_file)


export2json = export2json()
# Pré-requis :
# * disposer des bonnes configs dans le fichier /config/settings.ini
# * Avoir préalablement lancé `python 3 panopto2pod.py' pour remplir la BDD locale
# Lancer ensuite plusieurs fois ce script en retirant les commantaire de chaque étape ci-dessous :

# étape 1 : exporter les utilisteurs vers Pod
# export2json.exportUsers()

# étape 2 : depuis pod, importer le json obtenu ci-dessus

# étape 3 : remplacer les ids utilisateurs de la base locale par ceux de Pod.
# export2json.synchroPodUsers()

# Quand on est certains de tous nos ids utilisateurs, on exporte les vidéos
# export2json.exportPods()
