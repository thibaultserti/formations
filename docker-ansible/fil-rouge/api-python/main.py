# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging
import pymysql

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None

# Récupérer les informations de connexion depuis les variables d'environnement
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'password')
db_name = os.environ.get('DB_NAME', 'mydatabase')

# Fonction pour établir la connexion à la base de données
def get_db_connection():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Create table items

try:
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS items (name VARCHAR(255) NOT NULL, description TEXT);")
            result = cursor.fetchone()
    finally:
        connection.close()
except pymysql.err.OperationalError as e:
    logging.error(f"Cannot connect to database: {e}")

@app.get("/")
async def health():
    return {"Status": "OK"}

# Endpoint pour lire la version de MySQL
@app.get("/version")
async def read_version():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
            return {"Version de MySQL": result[0]}
    finally:
        connection.close()

# Endpoint pour ajouter un élément à la base de données
@app.post("/items/")
async def create_item(item: Item):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO items (name, description) VALUES (%s, %s)", (item.name, item.description))
        connection.commit()
        return {"message": "Item ajouté avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout de l'item: {e}")
    finally:
        connection.close()

# Endpoint pour supprimer un élément de la base de données
@app.delete("/items/{item}")
async def delete_item(item: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM items WHERE name = %s", (item,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item non trouvé")
        connection.commit()
        return {"message": "Item supprimé avec succès"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la suppression de l'item: {e}"
        )
    finally:
        connection.close()
