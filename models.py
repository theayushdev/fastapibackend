from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255,nullable=False)
    quantity_in_stock = fields.IntField(default=0)
    quantity_sold = fields.IntField(default=0)
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    supplied_by = fields.ForeignKeyField("models.Supplier",related_name="good_supplied")
    revenue = fields.DecimalField(max_digits=20, decimal_places=2,default=0.00)
    description = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Supplier(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255,nullable=False)
    company = fields.CharField(max_length=255,nullable=False)
    address = fields.CharField(max_length=255,nullable=False)
    phone_number = fields.CharField(max_length=20,nullable=False)
    email = fields.CharField(max_length=255,nullable=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


# create pydantic models 
product_pydantic = pydantic_model_creator(Product,name="Product")
product_pydanticIn = pydantic_model_creator(Product,name="ProductIn",exclude_readonly=True)

supplier_pydantic = pydantic_model_creator(Supplier,name="Suppiler")
supplier_pydanticIn = pydantic_model_creator(Supplier,name="SuppilerIn",exclude_readonly=True)

