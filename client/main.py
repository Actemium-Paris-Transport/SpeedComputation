from email.mime import base
import fastapi as FastAPI
from pydantic import BaseModel
import uvicorn 
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Form,  File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import tenseal as ts
import base64
from helper_functions import *




app = FastAPI()
templates = Jinja2Templates(directory="./templates")
app.mount("/client/templates", StaticFiles(directory="./templates"), name="static")

origins = ["http://localhost:7500",
           "http://apt.he.fr:80",
           "http://apt.he.fr:7500",
           "http://localhost:7500/",
           "http://localhost:4040/"]


methods = ["POST", "GET"]

headers = ["Accept, Accept-Language, Content-Language , Content-Type"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = methods,
    allow_headers = headers    
)







@app.get('/client/', response_class=HTMLResponse)
def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
 

@app.get('/client/Key_Generation', status_code=200)
async def GenKey() :    
    context_public_bfv, secret_context_bfv  = create_ctx_bfv()
    context_public_ckks, secret_context_ckks  = create_ctx_ckks()

    return {"secret_key_bfv": secret_context_bfv , "public_context_bfv": context_public_bfv,
            "secret_key_ckks": secret_context_ckks , "public_context_ckks": context_public_ckks}








class encrypt_matricule(BaseModel):
    matricule1 : str
    matricule2 : str
    time1 : str
    time2 : str
    distance : int
    context_public_bfv : str
    context_public_ckks : str




@app.post('/client/encrypt', status_code=200)
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
        #decode the serialized context 
        ctx_bfv = ts.context_from(base64.a85decode(context_public_bfv))
        ctx_ckks = ts.context_from(base64.a85decode(context_public_ckks))
        print("deserialized contex into a ts.context object")
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



class decrypt_result(BaseModel):
    res_enc : str
    inv_speed : str
    secret_context_bfv : str
    secret_context_ckks : str



@app.post('/client/decrypt', status_code=200)
async def encrypt(param : decrypt_result):
    try : 
        enc_res_mult_seri = param.res_enc 
        enc_invspeed_seri = param.inv_speed
        secret_context_encode_bfv = param.secret_context_bfv
        secret_context_encode_ckks = param.secret_context_ckks
        print("got the required param's") 
    except : 
        print("error in receving the param's")
    
    try : 
        secret_context_bfv = ts.context_from(base64.a85decode(secret_context_encode_bfv))
        secret_context_ckks = ts.context_from(base64.a85decode(secret_context_encode_ckks))
        print("secret key is ready")
    except : 
        print("error in deseriallizing the secret key")

    try : 
        enc_res_mult = ts.lazy_bfv_vector_from(base64.b64decode(enc_res_mult_seri))
        enc_invspeed = ts.lazy_ckks_vector_from(base64.b64decode(enc_invspeed_seri))
        print("decoding the result of multiplication and the inverse speed")
    except : 
        print("error in decoding")

    try : 
        enc_res_mult.link_context(secret_context_bfv)
        enc_invspeed.link_context(secret_context_ckks)
        print("linking the encrypted features to the context")
    except : 
        print("error in linking the encrypted param's to secret context")

    # getting the sk
    sk_bfv = secret_context_bfv.secret_key()
    sk_ckks = secret_context_ckks.secret_key()
    
    #decrypting then computing
    res_mult = enc_res_mult.decrypt(sk_bfv)
    inv_speed = enc_invspeed.decrypt(sk_ckks)
    speed = 1/inv_speed[0]

    
    count = 0
    for i in range(len(res_mult)):
        if res_mult[i] == 1 :
            count+= 1
        else : 
            count = count
    

    return {
        "vehicule_speed" : speed,
        "res_mult" : count
    }





def start(host="0.0.0.0", port=8008):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start()