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


    