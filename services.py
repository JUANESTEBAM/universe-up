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

def administrar_chatbot(text, number, messageId, name):
    text = text.lower()
    lista = []
    print("mensaje del usuario: ", text)

    markRead = markRead_Message(messageId)
    lista.append(markRead)
    time.sleep(2)

    datos_a_guardar = {
        "mensaje_usuario": text,
        "numero_usuario": number,
        "mensaje_id": messageId,
        "nombre_usuario": name
    }

    collection.insert_one(datos_a_guardar)

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Rizos Felices."
        footer = "Rizos Felices"
        
        options = ["✅ diagnostico", "📅 Catálogo Productos"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed1", messageId)
        replyReaction = replyReaction_Message(number, messageId, "🫡")
        lista.append(replyReaction)
        lista.append(replyButtonData)

    elif respuesta_usuario == "✅ Sí, por supuesto":
            nombre, numero = obtener_nombre_y_numero()  # Función para obtener el nombre y el número del usuario
            almacenar_usuario(nombre, numero)
        
    elif "informacion general" in text:
        body = "¿Qué necesitas saber de nosotros?"
        footer = "Rizos Felices"
        options = ["Lugares", "Productos"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed2", messageId)
        lista.append(replyButtonData)
# 1 plasticidad
    elif "diagnostico" in text:
        body = "Responde las siguientes preguntas para obtener tu diagnóstico. ¿Su cabello tiene capacidad de formar fácilmente el rizo?"
        footer = "Plasticidad"
        options = ["claro", "muy dificil"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed3", messageId)
        lista.append(replyButtonData)

# 2 Permeabilidad
    elif "claro" in text:
        body = "¿Su cabello moja fácilmente?"
        footer = "Permeabilidad"
        options = ["por supuesto", "no, nunca"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed4", messageId)
        lista.append(replyButtonData)

    elif "muy dificil" in text:
        body = "¿Su cabello moja fácilmente?"
        footer = "Permeabilidad"
        options = ["por supuesto", "no, nunca"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed5", messageId)
        lista.append(replyButtonData)

# 3 Densidad
    elif "por supuesto" in text:
        body = "¿Cuál es la cantidad de cabello?"
        footer = "Densidad"
        options = ["poco", "mucho"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed6", messageId)
        lista.append(replyButtonData)
    elif "no, nunca" in text:
        body = "¿Cuál es la cantidad de cabello?"
        footer = "Densidad"
        options = ["poco", "mucho"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed7", messageId)
        lista.append(replyButtonData)
        
# 4 Porosidad
    elif "poco" in text:
        body = "¿Su cabello se satura fácilmente?, Sensación de pesades al aplicar producto."
        footer = "Porosidad"
        options = ["Si", "De ningún modo"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed8", messageId)
        lista.append(replyButtonData)
    elif "mucho" in text:
        body = "¿Su cabello se satura fácilmente?, Sensación de pesades al aplicar producto."
        footer = "Porosidad"
        options = ["Si", "De ningún modo"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed9", messageId)
        lista.append(replyButtonData)
        
# 5 Oleosidad
    elif "si" in text:
        body = "¿Cuanto se engrasa la piel cabelluda?"
        footer = "Oleosidad"
        options = ["Poca", "Mucha"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed10", messageId)
        lista.append(replyButtonData)
    elif "de ningún modo" in text:
        body = "¿Cuanto se engrasa la piel cabelluda?"
        footer = "Oleosidad"
        options = ["Poca", "Mucha"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed11", messageId)
        lista.append(replyButtonData)
        
# 6 Grosor de la hebra
    elif "poca" in text:
        body = "¿Que tan Gruesa es su hebra capilar?"
        footer = "Grosor de la hebra"
        options = ["Delgado", "Medio o Grueso"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed12", messageId)
        lista.append(replyButtonData)
    elif "mucha" in text:
        body = "¿Que tan Gruesa es su hebra capilar?"
        footer = "Grosor de la hebra"
        options = ["Delgado", "Medio o Grueso"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed13", messageId)
        lista.append(replyButtonData)
        
# 7 Textura
    elif "delgado" in text:
        body = "¿Que patron de rizo tiene tu cabello?"
        footer = "Textura"
        options = ["Ondulado", "Rizado", "Afro"]

        replyButtonData = buttonReply_Message(number, options, body, footer, "sed14", messageId)
        lista.append(replyButtonData)
        
    elif "medio o grueso" in text:
        body = "¿Que patron de rizo tiene tu cabello?"
        footer = "Textura"
        options = ["Ondulado", "Rizado", "Afro"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed15", messageId)
        lista.append(replyButtonData)
        
# Final del diagnostico
    elif "ondulado" in text:
        body = "¿Presione para terminar?"
        footer = "Final"
        options = ["Terminar"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed16", messageId)
        lista.append(replyButtonData)
        
    elif "rizado" in text:
        body = "¿Presione para terminar?"
        footer = "Final"
        options = ["Terminar"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed17", messageId)
        lista.append(replyButtonData)
        
    elif "afro" in text:
        body = "¿Presione para terminar?"
        footer = "Final"
        options = ["Terminar"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed18", messageId)
        lista.append(replyButtonData)
        
    elif "terminar" in text:
        body = "¿Presione para terminar?"
        footer = "Final"
        options = ["Terminar"]
        replyButtonData = buttonReply_Message(number, options, body, footer, "sed19", messageId)
        lista.append(replyButtonData)
                     
    # Manejo de otras posibles preguntas o respuestas
    else:
        data = text_Message(number, "Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
        lista.append(data)

    for item in lista:
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