# Liste les utilisateurs au format Pod, + les champs spécifiques à Panopto (panopto_name, panopto_id)
# `main_id` sert à faire le lien entre plusieurs comptes (on y stocke l'id principal).
# (Sur Panopto, un même utilisateur aura un compte différent pour chaque Moodle associé)
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) DEFAULT NULL,
  `last_name` varchar(30) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  `panopto_name` varchar(45) DEFAULT NULL,
  `panopto_id` varchar(37) NOT NULL,
  `main_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `panopto_id_UNIQUE` (`panopto_id`),
  UNIQUE KEY `panopto_name_UNIQUE` (`panopto_name`)
  CONSTRAINT `fk_mainid` FOREIGN KEY (`main_id`) REFERENCES `auth_user` (`id`) ON UPDATE CASCADE
) DEFAULT CHARSET=utf8;

# La table migration nous sert à définir la liste des vidéo à migrer
# (elle peut etre remplie par un formulaire php par exemple)
CREATE TABLE `migration` (
  `pod_id` int(11) NOT NULL,
  `asked_by` int(11) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `asked_at` datetime DEFAULT NULL,
  `state` int(11) DEFAULT NULL,
  `access_type` varchar(20) DEFAULT NULL,
  `last_change` datetime DEFAULT NULL,
  `comment` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`pod_id`),
  CONSTRAINT `fk_podid` FOREIGN KEY (`pod_id`) REFERENCES `pods_pod` (`id`) ON UPDATE CASCADE
) DEFAULT CHARSET=utf8;

# La table migration_excluded nous sert de liste noire de vidéos à ne pas migrer
CREATE TABLE `migration_excluded` (
  `pod_id` int(11) NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`pod_id`)
) DEFAULT CHARSET=utf8;

# La table panopto_session contient un miroir local de toutes les sessions Panopto
CREATE TABLE `panopto_session` (
  `id` varchar(37) NOT NULL,
  `Name` varchar(45) DEFAULT NULL,
  `Description` varchar(45) DEFAULT NULL,
  `Folder` varchar(37) DEFAULT NULL,
  `StartTime` datetime DEFAULT NULL,
  `Duration` int(11) DEFAULT NULL,
  `MostRecentViewPosition` int(11) DEFAULT NULL,
  `CreatorId` varchar(37) DEFAULT NULL,
  `CreatedBy` varchar(45) DEFAULT NULL,
  `PercentCompleted` varchar(45) DEFAULT NULL,
  `filesize` int(11) DEFAULT NULL,
  `PublicDownload` tinyint(4) DEFAULT NULL,
  `tags` varchar(45) DEFAULT NULL,
  `MP4Url` varchar(255) DEFAULT NULL,
  `State` varchar(45) DEFAULT NULL,
  `StatusMessage` varchar(45) DEFAULT NULL,
  `IsBroadcast` tinyint(4) DEFAULT NULL,
  `IsDownloadable` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8;

# Liste des sessions panopto au format Pod
# Une entrée pour chaque ligne de `panopto_session`
#  dont le champ `State` est "Complete"
CREATE TABLE `pods_pod` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `video` varchar(255) NOT NULL,
  `allow_downloading` tinyint(1) NOT NULL,
  `title` varchar(250) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `date_added` date NOT NULL,
  `date_evt` date DEFAULT NULL,
  `description` longtext NOT NULL,
  `view_count` int(10) unsigned NOT NULL,
  `duration` int(11) NOT NULL,
  `type_id` int(11) NOT NULL,
  `is_draft` tinyint(1) NOT NULL,
  `is_restricted` tinyint(1) NOT NULL,
  `password` varchar(50) DEFAULT NULL,
  `cursus` varchar(1) NOT NULL,
  `main_lang` varchar(2) NOT NULL,
  `last_modified` date DEFAULT NULL,
  `last_viewed` date DEFAULT NULL,
  `panopto_session` varchar(37) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `panopto_session_UNIQUE` (`panopto_session`),
  KEY `FK_owner_id_refs_id` (`owner_id`),
  KEY `FK_type_id_refs_id` (`type_id`),
  CONSTRAINT `pods_pod_ibfk_1` FOREIGN KEY (`panopto_session`) REFERENCES `panopto_session` (`id`),
  CONSTRAINT `FK_owner_id_refs_id` FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK_type_id_refs_id` FOREIGN KEY (`type_id`) REFERENCES `pods_type` (`id`)
) DEFAULT CHARSET=utf8;

# Types de vidéo (à faire correspondre avec vos types pod)
CREATE TABLE `pods_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `slug` varchar(100) NOT NULL,
  `description` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`),
  UNIQUE KEY `slug` (`slug`),
) DEFAULT CHARSET=utf8;

# Insert un premier type de vidéo
INSERT INTO `pods_type` (id, description, title, slug)
VALUES (1, "", "Other", "other");
