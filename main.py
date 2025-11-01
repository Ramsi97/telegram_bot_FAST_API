from fastapi import FastAPI


app = FastAPI()

@app.get('/')
def index():
    return {"data": {"name" : "remedan"}}

@app.get('/about')
def about():
    return {"data": {"kk":"student in Astu"}}

