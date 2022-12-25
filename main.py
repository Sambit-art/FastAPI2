import pymongo
import uvicorn
from bson.objectid import ObjectId
from fastapi import FastAPI
from pydantic import BaseModel, json

json.ENCODERS_BY_TYPE[ObjectId] = str
app = FastAPI()

# myclient = pymongo.MongoClient("mongodb://localhost:27017/")

myclient = pymongo.MongoClient("mongodb+srv://sambit:sambit@demo.2isk9.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["blogapp"]
mycol = mydb["posts"]


class Comment(BaseModel):
    comment: str
    userId: str
    postId: str


class InputPost(BaseModel):
    title: str
    body: str
    userId: str


class outputPost(BaseModel):
    title: str
    body: str


class User(BaseModel):
    username: str
    password: str


allpost = []


@app.get("/", tags=["posts"])
async def home():
    result = myclient['blogapp']['posts'].aggregate([{'$addFields': {'kk': {'$toObjectId': '$userId'}}},
        {'$lookup': {'from': 'users', 'localField': 'kk', 'foreignField': '_id', 'as': 'user'}},
        {'$unwind': {'path': '$comment', 'includeArrayIndex': 'string'}},
        {'$addFields': {'userget': {'$toObjectId': '$comment.userId'}}},
        {'$lookup': {'from': 'users', 'localField': 'userget', 'foreignField': '_id', 'as': 'commentuser'}}, {
            '$group': {'_id': '$_id', 'title': {'$first': '$title'}, 'body': {'$first': '$body'},
                'user': {'$first': {'$first': '$user'}},
                'comment': {'$push': {'comment': '$comment', 'user': {'$first': '$commentuser'}}}}}])

    # for doc in cur:
    #     result.append(doc)
    #     print(doc)
    return list(result)

    @app.get("/home")
    async def home():
        return {"status": True}


@app.post("/newPost", tags=["posts"])
async def addPost(post: InputPost):
    print(post.dict())
    rec = {"title": post.dict()['title'], "body": post.dict()['body'], "userId": post.dict()['userId'], "comment": []}
    print(rec)
    mycol.insert_one(rec)
    # print(post.json())
    # print(allpost)
    return {"status": True}


# @app.get("/{postid}", tags=["posts"])
# async def getPostById(postid: str):
#     return {"user": [i for i in mycol.find({"_id": ObjectId(postid)})]}


@app.post('/comment', tags=["comment", "posts"])
async def insertComment(cm: Comment):
    rec = {"comment": cm.dict()['comment'], "userId": cm.dict()['userId']}
    mycol.update_one({"_id": ObjectId(cm.dict()['postId'])}, {"$push": {"comment": rec}})
    print(rec)
    return 0


@app.post('/createuser', tags=['users'])
async def createUser(user: User):
    mydb['users'].insert_one(user.dict())
    return {"status": True}


@app.get("/getuserbyid", tags=['users'])
async def getUser(id: str):
    cur = mydb['users'].find({"_id": ObjectId(id)})
    return list(cur)


@app.put('/updateuserbyid', tags=['users'])
async def updateuserbyid(id: str, user: User):
    mydb['users'].update_one({"_id": ObjectId(id)}, {"$set": user.dict()})
    return True


@app.get('/getpostbyuser', tags=['users', 'posts'])
async def getpostbyuser(userid: str):
    cur = mydb['posts'].find({"userId": userid})
    return list(cur)


@app.delete('/deletecomment',tags=['comment'])
async def deletecomment(postid: str, comment: str, userid: str):
    cur = mydb['posts'].update_one({"_id": ObjectId(postid)},
        {"$pull": {"comment": {"$and": [{"comment": comment}, {"userId": userid}]}}})
    return {"status": True}

