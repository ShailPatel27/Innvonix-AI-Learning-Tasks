from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Product(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0)
    in_stock: bool = True


@app.post("/products")
def create_product(product: Product):
    return {"message": "Product received", "product": product}
