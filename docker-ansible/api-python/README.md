# API Python

Cette application fonctionne avec python 3.11 ou supérieur.

## Installation de venv

## Venv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Dependencies
```bash
pip3 install -r requirements.txt
```

## Configuration
Les variables d'environnements suivantes sont utilisées pour communiquer avec la base de données
- `DB_HOST` : IP ou hostname de la base de donnée
- `DB_USER` : utilisateur de la base de donnée
- `DB_PASSWORD` : mot de passe de la base de donnée
- `DB_NAME` : nom de la base de donnée

## Run

```bash
uvicorn main:app --host 0.0.0.0
```
