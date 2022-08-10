import fastapi as FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, FastAPI, HTTPException, Request, Response, Form,  File, UploadFile
from pydantic import BaseModel
import uvicorn ##ça ASGI

import tenseal as ts
import base64

app = FastAPI()
templates = Jinja2Templates(directory="./templates")
app.mount("/templates", StaticFiles(directory="./templates"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)






def create_ctx_bfv():
    ctx = ts.context(ts.SCHEME_TYPE.BFV, poly_modulus_degree=4096, plain_modulus=1032193)

    ctx.generate_galois_keys()

    #secret key serialization and saving
    secret_context = ctx.serialize(save_secret_key = True) #secret context
    secret_context_base85_bfv = base64.a85encode(secret_context)
    #public context saving and serializaitoepfn
    ctx.make_context_public() #make it public and drop the secret key
    public_context_base85_bfv = base64.a85encode(ctx.serialize())

    
    return public_context_base85_bfv,secret_context_base85_bfv

def create_ctx_ckks():
    context = ts.context(ts.SCHEME_TYPE.CKKS, 8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
    context.global_scale = pow(2, 40)
    context.generate_galois_keys()

    secret_context = context.serialize(save_secret_key=True) #secret context
    secret_context_base85_ckks = base64.a85encode(secret_context)

    context.make_context_public() #drop sk
    public_context_base85_ckks = base64.a85encode(context.serialize())

    return public_context_base85_ckks, secret_context_base85_ckks




@app.get('/', response_class=HTMLResponse)
def root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
 

@app.get('/Key_Generation', status_code=200)
async def GenKey() :    
    context_public_bfv, secret_context_bfv  = create_ctx_bfv()
    context_public_ckks, secret_context_ckks  = create_ctx_ckks()

    return {"secret_key_bfv": secret_context_bfv , "public_context_bfv": context_public_bfv,
            "secret_key_ckks": secret_context_ckks , "public_context_ckks": context_public_ckks}








def start(host="0.0.0.0", port=7500):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start()