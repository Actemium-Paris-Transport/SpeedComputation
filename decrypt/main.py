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




class decrypt_result(BaseModel):
    res_enc : str
    inv_speed : str
    secret_context_bfv : str
    secret_context_ckks : str



@app.post('/decrypt', status_code=200)
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



def start(host="0.0.0.0", port=8009):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start()