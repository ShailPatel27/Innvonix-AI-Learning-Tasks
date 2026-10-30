from fastapi import FastAPI, status

app = FastAPI()

products = []


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(name: str):
    product = {"id": len(products) + 1, "name": name}
    products.append(product)
    return product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    products[:] = [product for product in products if product["id"] != product_id]
