from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import (supplier_pydantic,supplier_pydanticIn,Supplier,product_pydantic,product_pydanticIn,Product)

# email

from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

# dot env 
from dotenv import dotenv_values
config = dotenv_values(".env")

# cors middelware 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# adding cors urls 
origins = [
    "http://localhost:5173",
    "https://theayushdev.github.io/fastapifront",
    "https://fastapibackend.onrender.com"
]

# add midellware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

@app.get('/')
def index():
    return {'message': 'Hello, World!'}  # Return a JSON response

@app.post('/supplier')
async def add_supplier(supplier_info: supplier_pydanticIn):
    supplier = await Supplier.create(**supplier_info.dict(exclude_unset=True))
    response = await supplier_pydanticIn.from_tortoise_orm(supplier)
    return {'status': 'ok','data': response}

@app.get('/supplier')
async def get_all_supplier():
    suppliers = await supplier_pydantic.from_queryset(Supplier.all())
    return {'status': 'ok','data': suppliers}

@app.get('/supplier/{id}')
async def get_supplier(id: int):
    supplier = await Supplier.get(id=id)
    response = await supplier_pydantic.from_queryset_single(supplier)
    return {'status': 'ok','data': response}

@app.put('/supplier/{id}')
async def update_supplier(id: int, update_info: supplier_pydanticIn):
    await Supplier.filter(id=id).update(**update_info.dict(exclude_unset=True))
    supplier = await Supplier.get(id=id)
    response = await supplier_pydanticIn.from_tortoise_orm(supplier)
    return {'status': 'ok', 'data': response}

@app.delete('/supplier/{id}')
async def delete_supplier(id: int):
    await Supplier.filter(id=id).delete()
    return {'status': 'ok'}

@app.post('/product/{supplier_id}')
async def add_product(supplier_id: int, product_info: product_pydanticIn):
    supplier = await Supplier.get(id=supplier_id)
    product_info = product_info.dict(exclude_unset = True)
    product_info['revenue'] += product_info['price'] * product_info['quantity_sold']
    product_obj = await Product.create(**product_info, supplied_by=supplier)
    response = await product_pydanticIn.from_tortoise_orm(product_obj)
    return {'status': 'ok', 'data': response}

@app.get('/product')
async def get_all_product():
    products = await product_pydantic.from_queryset(Product.all())
    return {'status': 'ok', 'data': products}

@app.get('/product/{id}')
async def get_product(id: int):
    product =  await Product.get(id=id)
    response = await product_pydantic.from_queryset_single(product)
    return {'status': 'ok', 'data': response}

@app.put('/product/{id}')
async def update_product(id: int, update_info: product_pydanticIn): 
    
    product = await Product.get(id=id)
    update = update_info.dict(exclude_unset = True)
    product.name = update['name']
    product.price = update['price']
    product.quantity_sold += update['quantity_sold']
    product.revenue += update['price'] * update['quantity_sold']
    product.quantity_in_stock = update['quantity_in_stock']
    await product.save()
    response = await product_pydanticIn.from_tortoise_orm(product)
    return {'status': 'ok', 'data': response}

@app.delete('/product/{id}')
async def delete_product(id: int):
    await Product.filter(id=id).delete()
    return {'status': 'ok'}



class EmailSchema(BaseModel):
    email: List[EmailStr]

class EmailContent(BaseModel):
    subject: str
    body: str



conf = ConnectionConfig(
    MAIL_USERNAME = config['EMAIL'],
    MAIL_PASSWORD = config['PASS'],
    MAIL_FROM = config['EMAIL'],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

@app.post('/email/{product_id}')
async def send_email(product_id: int,  email_content: EmailContent):
    product = await Product.get(id=product_id).select_related("supplied_by")
    supplier = product.supplied_by
    supplier_email = [supplier.email]



    html = f"""
    <h5>Ayush Bussines pvt ltd </h5>
    <br>
    <p>{email_content.body}</p>
    """


    message = MessageSchema(
        subject=email_content.subject,
        recipients=supplier_email,
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return {'status': 'ok'}

register_tortoise(
    app,
    db_url="sqlite://database.sqllite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)