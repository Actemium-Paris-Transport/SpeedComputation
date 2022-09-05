from email.mime import base
import fastapi as FastAPI
from pydantic import BaseModel
import uvicorn 
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Form,  File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import tenseal as ts
import base64
from helper_functions import *




app = FastAPI()


origins = ["http://localhost:7500",
           "http://apt.he.fr:80",
           "http://apt.he.fr:7500",
           "http://localhost:7500/",
           "http://localhost:4040/"]


methods = ["POST"]

headers = ["Accept, Accept-Language, Content-Language , Content-Type"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = methods,
    allow_headers = headers    
)

class encrypt_matricule(BaseModel):
    matricule1 : str
    matricule2 : str
    time1 : str
    time2 : str
    distance : int
    context_public_bfv : str
    context_public_ckks : str




@app.post('/encrypt', status_code=200)
async def encrypt(param : encrypt_matricule):
    try :
        mat_1 = param.matricule1
        mat_2 = param.matricule2
        t_1 = param.time1
        t_2 = param.time2
        d = param.distance
        context_public_bfv = param.context_public_bfv
        context_public_ckks = param.context_public_ckks
        

    except : 
        print("problem in receiving")

    #pre-process
    matri_1 , matri_2  ,time_1 , time_2 , distance = infromations(mat_1, mat_2, t_1 , t_2 , d)

    try : 
        ctx_bfv = ts.context_from(base64.a85decode(context_public_bfv))
        ctx_ckks = ts.context_from(base64.a85decode(context_public_ckks))
        print("deserialized contox into a ts.context object")
    except :
        print("problem in converting from b64 str to ts.context")


    try : 
        enc_mat1= ts.bfv_vector(ctx_bfv,matri_1 )
        enc_mat2 = ts.bfv_vector(ctx_bfv,matri_2 )

        enc_time_1 = ts.ckks_vector(ctx_ckks,time_1 )
        enc_time_2 = ts.ckks_vector(ctx_ckks,time_2 )
        print("encryption done with succes")
    except :
        print("error in encryption")

    try :
        enc_mat1_bytes = base64.b64encode(enc_mat1.serialize())
        enc_mat2_bytes = base64.b64encode(enc_mat2.serialize())    

        enc_time_1_bytes = base64.b64encode(enc_time_1.serialize())
        enc_time_2_bytes = base64.b64encode(enc_time_2.serialize())

        print("serialization done")
    except : 
        print("error in serialization ")
    
    
    return {
        "enc_matricule_1" : enc_mat1_bytes,
        "enc_matricule_2" : enc_mat2_bytes,
        "enc_time_1" : enc_time_1_bytes,
        "enc_time_2" : enc_time_2_bytes,
        "distance" : distance
    }









def start(host="0.0.0.0", port=8008):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start()