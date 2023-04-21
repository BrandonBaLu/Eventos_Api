from fastapi import Depends, FastAPI , HTTPException, status, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import pyrebase
from fastapi.middleware.cors import CORSMiddleware
from typing import List


app = FastAPI()


class Respuesta (BaseModel) :  
    message: str  


class Evento (BaseModel) :  
    Nombre: str
    Fecha: str
    Hora: str
    Lugar: str
    Costo: int
    Descripcion: str
    Imagen: str

class EventoUpdate (BaseModel) :  
    id_evento: str
    Nombre: str
    Fecha: str
    Hora: str
    Lugar: str
    Costo: int
    Descripcion: str
    Imagen: str


class UserIN(BaseModel):
    email       : str
    password    : str
    

origins = [
    "*",   
    "http://68.183.67.194/",
            
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hola"}

firebaseConfig = {
  "apiKey": "AIzaSyCuJuJULBMQWVhUWXYEOHsg3FMAEeDRVM0",
  "authDomain": "mipaginaweb-d1d99.firebaseapp.com",
  "databaseURL": "https://mipaginaweb-d1d99-default-rtdb.firebaseio.com",
  "projectId": "mipaginaweb-d1d99",
  "storageBucket": "mipaginaweb-d1d99.appspot.com",
  "messagingSenderId": "953627572865",
  "appId": "1:953627572865:web:c303735d5d069efcfeeb80",
   "measurementId": "G-9L3DBHCJR0"
};

firebase = pyrebase.initialize_app(firebaseConfig)


securityBasic  = HTTPBasic()
securityBearer = HTTPBearer()


#Autenticacion
@app.post(
    "/users/token",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Consigue un token para el usuario",
    description="Consigue un token para el usuario",
    tags=["auth"],
)

async def post_token(credentials: HTTPBasicCredentials = Depends(securityBasic)):
    try:
        email = credentials.username
        password = credentials.password
        auth = firebase.auth()
        user = auth.sign_in_with_email_and_password(email, password)
        #trae el level del usuario
        db=firebase.database()
        level = db.child("users").child(user["localId"]).child("level").get().val()
        
        response = {
            "message": "Usuario autenticado",
            "token": user["idToken"],
            "level": level,
            "code": status.HTTP_201_CREATED,
        }
        return response
    except Exception as error:
        print(f"Error: {error}")
        return(f"Error: {error}")
    
#Crea un usuario en la base de datos firebase para clientes
@app.post(  "/registro/",  
    status_code=status.HTTP_202_ACCEPTED, 
    summary="Crea un usuario para clientes",
    description="Crea un usuario para clientes", 
    tags=["auth"]
)
async def create_user(usuario: UserIN ):
    try:
        auth = firebase.auth()
        db=firebase.database()
        user = auth.create_user_with_email_and_password(usuario.email, usuario.password)
        uid = user["localId"]
        db.child("users").child(uid).set({"email": usuario.email, "level": 0 })
        response = {"code": status.HTTP_201_CREATED, "message": "Usuario creado"}
        return response
    except Exception as error:
        print(f"Error: {error}")
        return(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
#Crea un usuario en la base de datos firebase para administradores
@app.post(  "/users/",  
    status_code=status.HTTP_202_ACCEPTED, 
    summary="Crea un usuario para administradores",
    description="Crea un usuario para administradores", 
    tags=["auth"]
)
async def create_user(usuario: UserIN ):
    try:
        auth = firebase.auth()
        db=firebase.database()
        user = auth.create_user_with_email_and_password(usuario.email, usuario.password)
        uid = user["localId"]
        db.child("users").child(uid).set({"email": usuario.email, "level": 1, "nombre": "admin"})
        response = {"code": status.HTTP_201_CREATED, "message": "Usuario creado"}
        return response
    except Exception as error:
        print(f"Error: {error}")
        return(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

#Obtiene un usuario por su id
@app.get(
    "/usuarios/{id_usuario}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regresa un usuario",
    description="Regresa un usuario"
)
async def get_usuarios(id_usuario: str):
    try:
        db=firebase.database()
        usuario = db.child("users").child(id_usuario).get().val()
        response = {
            "usuario": usuario
        }
        return response
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permiso para ver estos datos",
            headers={"WWW-Authenticate": "Basic"},        
        )
    
#Obtiene una lista de usuarios
@app.get(
    "/usuarios/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regresa una lista de usuarios",
    description="Regresa una lista de usuarios"
)
async def get_usuarios():
    try:
        db=firebase.database()
        usuarios = db.child("users").get().val()
        response = {
            "usuarios": usuarios
        }
        return response
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permiso para ver estos datos",
            headers={"WWW-Authenticate": "Basic"},        
        )
    


#Obtiene una lista de eventos registrados
@app.get(
    "/eventos/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regresa una lista de eventos",
    description="Regresa una lista de eventos"
)
async def get_eventos():
    try:
        db=firebase.database()
        eventos = db.child("Eventos").get().val()
        response = {
            "eventos": eventos
        }
        return response
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permiso para ver estos datos",
            headers={"WWW-Authenticate": "Basic"},        
        )

#Obtiene un evento por su id
@app.get(
    "/eventos/{id_evento}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regresa un evento",
    description="Regresa un evento"
)
async def get_eventos(id_evento: str):
    try:
        db=firebase.database()
        evento = db.child("Eventos").child(id_evento).get().val()
        response = {
            "evento": evento
        }
        return response
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No tienes permiso para ver estos datos",
            headers={"WWW-Authenticate": "Basic"},        
        )
    
#Agrega un evento 
@app.post("/eventos/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Inserta un evento",
    description="Inserta un evento",
    tags=["auth"]
)
async def post_eventos(evento: Evento, credentials: HTTPAuthorizationCredentials = Depends(securityBearer)):
    try:
        auth = firebase.auth()
        user = auth.get_account_info(credentials.credentials)
        uid  = user["users"][0]["localId"]
        db=firebase.database()
        usuario = db.child("users").child(uid).get().val()
        level = usuario["level"]
        #print(usuario)
        if  level == 1:
            db.child("Eventos").push({"Nombre": evento.Nombre, "Fecha": evento.Fecha, "Lugar": evento.Lugar, "Costo": evento.Costo, "Descripcion": evento.Descripcion, "Hora": evento.Hora, "Imagen": evento.Imagen})
            response = {
                "code": status.HTTP_201_CREATED, 
                "message": "Evento creado",
                "level": level
                }
            return response
        else:
            detail="No tienes permiso para agregar eventos",
            return detail
   
    except Exception as error:
        print(f"Error: {error}")
        return(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    
#Actualiza un evento
@app.put(
    "/eventos/",
    response_model=Respuesta,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Actualiza un evento",
    description="Actualiza un evento",
    tags=["auth"]
)
async def put_eventos(evento: EventoUpdate, credentials: HTTPAuthorizationCredentials = Depends(securityBearer)):
    try:
        auth = firebase.auth()
        user = auth.get_account_info(credentials.credentials)
        uid  = user["users"][0]["localId"]  
        db=firebase.database()
        usuario = db.child("users").child(uid).get().val()
        level = usuario["level"]
        id=evento.id_evento
        if  level == 1:
            db.child("Eventos").child(id).update({"Nombre": evento.Nombre, "Fecha": evento.Fecha, "Lugar": evento.Lugar, "Costo": evento.Costo, "Descripcion": evento.Descripcion, "Hora": evento.Hora, "Imagen": evento.Imagen})
            response = {
                "message":"Evento actualizado"
            }
            return response
        else:
            detail="No tienes permiso para actualizar eventos",
            return detail   
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED           
        )
    
#Elimina un evento
@app.delete(
    "/eventos/{id_evento}",
    response_model=Respuesta,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Elimina un evento",
    description="Elimina un evento",
    tags=["auth"]
)
async def delete_eventos(id_evento: str, credentials: HTTPAuthorizationCredentials = Depends(securityBearer)):
    try:
        auth = firebase.auth()
        user = auth.get_account_info(credentials.credentials)
        uid  = user["users"][0]["localId"]
        db=firebase.database()
        usuario = db.child("users").child(uid).get().val()
        level = usuario["level"]
        if  level == 1:
            db.child("Eventos").child(id_evento).remove()
            response = {
                "message":"Evento eliminado"
            }
            return response
        else:
            detail="No tienes permiso para eliminar eventos",
            return detail
    except Exception as error:
        print(f"Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED           
        )