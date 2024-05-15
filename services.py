import requests
import sett
import json
import time
import openai
from pymongo import MongoClient






client=MongoClient('localhost',27017)

try:
    database=client['universe_python']

    collection=database['datauser']

    documents=collection.find()
    
    for document in documents:
        print(document)

    
except Exception as ex:
    print("error de conexión:{}".format(ex))

    client.close()
finally:
    print("conexion Finalizada")



def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data

def get_media_id(media_name , media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    #elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    #elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    #elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {
                "message_id": messageId,
                "emoji": emoji
            }
        }
    )
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": { "message_id": messageId },
            "type": "text",
            "text": {
                "body": text
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data
  
usuarios = {}
respuesta_usuarios= {}


  
def administrar_chatbot(text,number, messageId, name):
    text = text.lower() #mensaje que envio el usuario
    list = []
    print("mensaje del usuario: ",text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    datos_a_guardar = {
        "mensaje_usuario": text,
        "numero_usuario": number,
        "mensaje_id": messageId,
        "nombre_usuario": name
    }

    collection.insert_one(datos_a_guardar)

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Rizos Felices. ¿Cómo podemos ayudarte hoy?"
        footer = "Rizos Felices"
        options = ["✅ diagnostico", "📅 Catálogo Productos"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        list.append(replyReaction)
        list.append(replyButtonData)
        
        
        
        
    elif "diagnostico" in text:
        body = "Responde las siguientes preguntas para obtener tu diagnostico. ¿EL CABELLO TIENE CAPACIDAD DE FORMAR FACILMENTE EL RIZO ?"
        footer = "Plasticidad"
        options = ["Si", "No"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2",messageId)
        sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

        list.append(replyButtonData)
        
      
        
    elif  "si" in text:  
         body = "EL CABELLO MOJA FÁCILMENTE?"
         footer = "Permeabilidad"
         options = ["✅ Sí", "⛔ No"]

         replyButtonData = buttonReply_Message(number, options, body, footer, "sed3", messageId)
         list.append(replyButtonData) 
            
    elif "no" in text: 
            # Hacer la siguiente pregunta sobre densidad
            body = "¿Cuál es la cantidad de cabello?"
            footer = "Densidad"
            options = ["poco", "Mucho"]
            
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed4", messageId)
            list.append(replyButtonData)  
            
        
        
        
    elif "poco" in text: 
            # Hacer la siguiente pregunta sobre densidad
            body = "¿Cuál es la cantidad de cabellos?"
            footer = "Densidad"
            options = ["poco", "Mucho"]
            
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed4", messageId)
            list.append(replyButtonData)  
            
    elif "mucho" in text: 
            # Hacer la siguiente pregunta sobre densidad
            body = "¿Cuál es la cantidad de cabello2?"
            footer = "Densidad"
            options = ["si", "no"]
            
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed4", messageId)
            list.append(replyButtonData)  
            
    elif "si" in text: 
            # Hacer la siguiente pregunta sobre densidad
            body = "¿Cuál es la cantidad de cabello5?"
            footer = "Densidad"
            options = ["poco", "Mucho"]
            
            replyButtonData = buttonReply_Message(number, options, body, footer, "sed4", messageId)
            list.append(replyButtonData)         
        
   
    # También podrías enviar una lista de productos recomendados, etc.
    else:
        data = text_Message(number, "Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)

        






#indicador añadido para envio mensajes
def replace_start(s):
    number = s[3:]
    if s.startswith("57"):
        return "573" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
        

