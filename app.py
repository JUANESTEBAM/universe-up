from pymongo import MongoClient
from flask import Flask, request
import sett
import services

app = Flask(__name__)

# Almacena tus credenciales en variables
username = "1129804613"
password = "1129804613"
# Construye la URL de conexión utilizando las variables de credenciales
url = f"mongodb+srv://{username}:{password}@cluster0.farnu1a.mongodb.net/mydatabase?retryWrites=true&w=majority"
# Crea el cliente de MongoDB
client = MongoClient(url)
# Selecciona la base de datos y la colección
db = client['mydatabase']
collection = db['mycollection']
# Define el documento a insertar
document = {"name": "sk", "city": "bengaluru"}
# Inserta el documento en la colección
inserted_document = collection.insert_one(document)
# Imprime el ID del documento insertado
print(f"Inserted Document ID: {inserted_document.inserted_id}")
# Cierra la conexión con la base de datos
client.close()

@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    return 'Hola mundo '

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = services.replace_start(message['from'])
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)

        services.administrar_chatbot(text, number,messageId,name)
        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)

if __name__ == '__main__':
    app.run()
