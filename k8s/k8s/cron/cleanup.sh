#!/bin/bash
set -e # Quitte si une commande échoue

echo "[$(date)] --- Démarrage du Job de Nettoyage ---"

# Variables d'env fournies par K8s Secrets/ConfigMaps
# PGHOST, PGUSER, PGPASSWORD, PGDATABASE sont utilisées nativement par psql

# Test de connexion simple
if ! pg_isready; then
    echo "ERREUR: Impossible de joindre la base de données."
    exit 1
fi

echo "DB connectée. Suppression des messages vieux de plus de 5 minutes..."

# Exécution de la requête SQL
# On supprime les messages où 'created_at' est plus vieux que 'maintenant moins 5 minutes'
DELETED_COUNT=$(psql -t -c "DELETE FROM messages WHERE created_at < NOW() - INTERVAL '5 minutes';")

echo "Succès : $DELETED_COUNT anciens messages supprimés."
echo "[$(date)] --- Fin du Job ---"