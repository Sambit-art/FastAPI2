from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
app=FastAPI()



class InputPost(BaseModel):
    title:str
    body:str
    userId:int
    postId:int

class outputPost(BaseModel):
    title: str
    body: str

allpost=[
    InputPost(title='first post title', body='first post body', userId=0,postId=1),
    InputPost(title='second post title', body='second post body', userId=0,postId=2)]


@app.get("/")
async def home():
    return {"hello":"world"}

@app.post("/new",response_model=outputPost)
async def addPost(post:InputPost):
    allpost.append(post)
    print(allpost)
    return post

@app.get("/{postid}",response_model=outputPost)
async def getPostById(postid:int):
    for item in allpost:
        if(item.postId==postid):
            return item
    return {item:item}
