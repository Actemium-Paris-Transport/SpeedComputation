from email.mime import base
import fastapi as FastAPI
from pydantic import BaseModel
import uvicorn 
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Form,  File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import tenseal as ts
import base64
import time



app = FastAPI()

#app.mount("/static", StaticFiles(directory="static"), name="static")

#templates = Jinja2Templates(directory="./templates")

origins = ["*"]
methods = ["*"]
headers = ["*"]


app.add_middleware(
    CORSMiddleware, 
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = methods,
    allow_headers = headers    
)



class Params(BaseModel):
    context_public_bfv: str
    context_public_ckks: str 
    mat_1_seri_bytes: str
    mat_2_seri_bytes: str
    t_1_seri_bytes: str
    t_2_seri_bytes: str
    dist : list

@app.post('/inference', status_code=200)
async def encrypt(param : Params):
    
    mat_1_seri_bytes = param.mat_1_seri_bytes
    mat_2_seri_bytes = param.mat_2_seri_bytes
    t_1_seri_bytes = param.t_1_seri_bytes
    t_2_seri_bytes = param.t_2_seri_bytes
    d = param.dist
    context_public_seri_bfv = param.context_public_bfv
    context_public_seri_ckks = param.context_public_ckks
    

    #decode params
    context_public_bfv = ts.context_from(base64.a85decode(context_public_seri_bfv)) #turn it into ts.bfv.context object
    context_public_ckks = ts.context_from(base64.a85decode(context_public_seri_ckks))

    mat_1 = ts.lazy_bfv_vector_from(base64.b64decode(mat_1_seri_bytes))
    mat_2 = ts.lazy_bfv_vector_from(base64.b64decode(mat_2_seri_bytes))

    t_1 =  ts.lazy_ckks_vector_from(base64.b64decode(t_1_seri_bytes))
    t_2 =  ts.lazy_ckks_vector_from(base64.b64decode(t_2_seri_bytes))

    #linking to context
    mat_1.link_context(context_public_bfv)
    mat_2.link_context(context_public_bfv)

    t_1.link_context(context_public_ckks)
    t_2.link_context(context_public_ckks)

    start_time = time.time()
    # start computing
    enc_res_mult = mat_1 * mat_2
    time_diff = t_2 - t_1
    invspeed = time_diff * d
    end_time = time.time()

    enc_res_mult_seri = base64.b64encode(enc_res_mult.serialize())
    invspeed_seri = base64.b64encode(invspeed.serialize())
    infrenece_time = end_time - start_time
    

    return {
        "res_mult" : enc_res_mult_seri,
        "inverse_speed" : invspeed_seri,
        "inference_time": infrenece_time
    }

def start(host="0.0.0.0", port=8000):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start()