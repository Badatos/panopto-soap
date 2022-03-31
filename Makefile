
install:
	python3 -m pip install -r requirements.txt

createDB:
	mysql -D panopto2pod < data/migration_db.sql

# Importe les sessions de Panopto dans une BDD locale
import_sessions:
	python3 src/panopto2pod.py

# Exporte les sessions de la BDD locale vers des fichiers JSON compatibles avec Esup-Pod
export_json:
	python3 src/db2json.py


