from pymongo import MongoClient
from flask import Flask, request
import sett
import services
from pymongo import MongoClient

app = Flask(__name__)

# Almacena tus credenciales en variables
username = "luisafbs3"
password = "Fionna5109"
# Construye la URL de conexión utilizando las variables de credenciales
url = f"mongodb+srv://{username}:{password}@cluster0.skcoldx.mongodb.net/universe_python?retryWrites=true&w=majority&appName=Cluster0"
# Crea el cliente de MongoDB
client = MongoClient(url)
# Selecciona la base de datos y la colección
db = client['universe_python']
collection = db['chats']

app = Flask(__name__)

# Almacena tus credenciales en variables

@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    return 

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
        
        

        chat_document = {
            "number": number,
            "name": name,
            "messageId": messageId,
            "text": text,
            "response": None,
             
            
            
        }
        
        # Inserta el documento en la colección 'chats' de MongoDB
        inserted_document = collection.insert_one(chat_document)
        # Imprime el ID del documento insertado
        print(f"Inserted Chat Document ID: {inserted_document.inserted_id}")
        
        services.administrar_chatbot(text, number,messageId,name)
        
           
             

        return 'enviado'

      
      
    except Exception as e:
        return 'no enviado ' + str(e)

if __name__ == '__main__':
    app.run()

