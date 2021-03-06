from flask import Flask, json, request
from pymongo import MongoClient

USER = "grupo2"
PASS = "grupo2"
DATABASE = "grupo2"

URL = f"mongodb://{USER}:{PASS}@gray.ing.puc.cl/{DATABASE}?authSource=admin"
client = MongoClient(URL)

# MENSAJES
MESSAGE_KEYS = ['date', 'lat', 'long',
                'message', 'receptant', 'sender']
# TEXT-SEARCH
SEARCH_KEYS = ['desired', 'required', 'forbidden', 'userId']
# NO RESULTS
no_results = {"success": True, "results": "empty", "reason": "no results"}
# NO USER ID
no_user_id = {"success": True, "results": "empty", "reason": "no user ID"}
# Nombre bbd
db = client["grupo2"]

app = Flask(__name__)


@app.route("/")
def home():
    '''
    Página de inicio
    '''
    return "<h1>¡Hola!</h1>"


@app.route("/users")
def get_users():
    '''
        usuarios.find({}, {_id: 0})
    '''
    users = list(db.usuarios.find({}, {"_id": 0}))

    return json.jsonify(users)


@app.route("/users/<int:uid>")
def get_user(uid):
    '''
        usuarios.find({}, {"_id": 0})
    '''
    users = list(db.usuarios.find({"uid": uid}, {"_id": 0}))

    if users: 
        return json.jsonify(users)
    else: 
        return json.jsonify('uid no identificado')



@app.route("/messages")
def get_messages():
    '''
        mensajes.find({}, {_id: 0})
    '''
    uid1 = request.args.get("id1", False)
    uid2 = request.args.get("id2", False)
    if uid1 and uid2:
        m1 = list(db.mensajes.find({"$or":[{"sender": int(uid1), "receptant": int(uid2)}, {"sender": int(uid2), "receptant": int(uid1)}]}, {"_id": 0}))
        return json.jsonify(m1)
    else:
        messages = list(db.mensajes.find({}, {"_id": 0}))
        return json.jsonify(messages)


@app.route("/messages/<int:mid>")
def get_message(mid):
    '''
        mensajes.find({}, {"_id": 0})
    '''
    messages = list(db.mensajes.find({"mid": mid}, {"_id": 0}))
    
    if messages:
        return json.jsonify(messages)
    else: 
        return json.jsonify('mid no identificado')


@app.route("/sent/<int:uid>")
def get_sent(uid):

    messages = list(db.mensajes.find({"sender": uid}, {"_id": 0}))
    
    if messages:
        return json.jsonify(messages)
    else: 
        return json.jsonify('uid no identificado')

@app.route("/recieved/<int:uid>")
def get_recieved(uid):

    messages = list(db.mensajes.find({"receptant": uid}, {"_id": 0}))
    
    if messages:
        return json.jsonify(messages)
    else: 
        return json.jsonify('uid no identificado')


@app.route("/messages", methods=['POST'])
def create_message():

    data = {key: request.json[key] for key in MESSAGE_KEYS}
    
    lista_sucia = list(db.mensajes.find({}, {"mid": 1}))
    lista_limpia = []
    for dicc in lista_sucia:
        if 'mid' in dicc.keys(): 
            lista_limpia.append(dicc['mid'])
    lista_limpia.sort()
    mid = lista_limpia[-1] + 1
    data['mid'] = mid
    result = db.mensajes.insert_one(data).inserted_id

    return json.jsonify({"success": True})


@app.route("/message/<int:mid>", methods=['DELETE'])
def delete_message(mid):
    messages = list(db.mensajes.find({"mid": mid}, {"_id": 0}))
    if messages:
        db.mensajes.remove({"mid": mid})
        return json.jsonify({"success": True})

    else: 
        return json.jsonify('mid no identificado')





def get_query(data):
    #en caso de que no haya una key
    for key in SEARCH_KEYS:
        if key not in data.keys():
            data[key] = []
 
    print('data:', data)

    forbidden = data["forbidden"]
    desired = data["desired"]
    required = data["required"]

    #en caso de que el value de la key sea lista vacia
    if desired == []:
        desired = ""
    else:
        desired = (" ").join(desired)

    if required == []:
        required = ""
    else:
        required = ["\"" + x + "\"" for x in required]
    
    if forbidden == []:
        forbidden = ""
    else:
        forbidden = "-" + (" -").join(forbidden)



    return desired, required, forbidden

@app.route("/text-search")
def search_message():
    data = request.json
    if not data or data == None:
        print('no hay body o es dict vacio')
        mensajes_all = list(db.mensajes.find({},{"_id": 0}))
        return json.jsonify(mensajes_all)
    desired, required, forbidden = get_query(data)

    # Ver si solo hay forbiddens
    # Hacer dos consultas, una con todos los mensajes y otros con los que
    # contengan la palabra prohibida, y restar los conjuntos.
    # " \"required" "desired" -"forbidden" "
    if desired == "" and required == "" and forbidden != "":
        print('solo hay forbidden')
        # forbidden_lista = forbidden.replace("-", "").split(" ")
        query = forbidden.replace("-", "")
        if type(data["userId"]) == int:
            mensajes_all = list(db.mensajes.find({"$or":[{"sender": data["userId"]}, {"receptant": data["userId"]}]},{"_id": 0}))
            if not mensajes_all:
                return json.jsonify(no_results)
            mensajes_forbidden = list(db.mensajes.find({"$text": {"$search": query}, "$or":[{"sender": data["userId"]}, {"receptant": data["userId"]}]}, {"_id": 0}))
            print(mensajes_forbidden)

            # Restar listas
            mensajes = []
            for mensaje in mensajes_all:
                if mensaje not in mensajes_forbidden:
                    mensajes.append(mensaje)

            return json.jsonify(mensajes)
        else:
            mensajes_all = list(db.mensajes.find({},{"_id": 0}))
            if not mensajes_all:
                return json.jsonify(no_results)
            mensajes_forbidden = list(db.mensajes.find({"$text": {"$search": query}}, {"_id": 0}))

            # Restar listas
            mensajes = []
            for mensaje in mensajes_all:
                if mensaje not in mensajes_forbidden:
                    mensajes.append(mensaje)
            
            return json.jsonify(mensajes)

    elif desired == "" and required == "" and forbidden == "":
        print('body values todos vacios')

        if type(data["userId"]) == int:
            mensajes_all = list(db.mensajes.find({"$or":[{"sender": data["userId"]}, {"receptant": data["userId"]}]},{"_id": 0}))
            if not mensajes_all:
                return json.jsonify(no_results)
            return json.jsonify(mensajes_all)
        else:
            mensajes_all = list(db.mensajes.find({}, {"_id": 0}))
            return json.jsonify(mensajes_all)
    else:
        print('body normal')
        query = f"{required} {desired} {forbidden}"

        if type(data["userId"]) == int:
            mensajes = list(db.mensajes.find({"$text": {"$search": query}, "$or":[{"sender": data["userId"]}, {"receptant": data["userId"]}]}, {"_id": 0}))
            if not mensajes:
                return json.jsonify(no_results)
            return json.jsonify(mensajes)
        else:
            mensajes = list(db.mensajes.find({"$text": {"$search": query}}, {"_id": 0}))
            return json.jsonify(mensajes)


app.config['DEBUG'] = True

if __name__ == '__main__':
    app.run()