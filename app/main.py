import app.social as sn
import random
from random import randrange
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel


not_authorized = "You are not authorized to perform that operation"


app = FastAPI()


class UserSchema(BaseModel):
    user_name: str
    password: str


class SessionSchema(BaseModel):
    user_name: str
    token: int


class NewPasswordSchema(SessionSchema):
    new_password: str


class PostSchema(SessionSchema):
    content: str


users = dict()
sessions = dict()  # user_name -> token


def auth(user_name, token):
    return user_name in sessions and token == sessions[user_name]


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(new_user: UserSchema):
    if new_user.user_name not in users:
        user_instance = sn.User(new_user.user_name, new_user.password)
        users[new_user.user_name] = user_instance
        return {"data": {"username": new_user.user_name}}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"The username {new_user.user_name} already exists")


@app.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: UserSchema):
    if credentials.user_name in users:
        this_user: sn.User = users[credentials.user_name]
        if this_user.authenticate(credentials.password):
            token = random.randint(0, 9999999)
            sessions[credentials.user_name] = token
            return {"data": {"username": credentials.user_name, "token": token}}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Access denied")


@app.post("/newpassword", status_code=status.HTTP_202_ACCEPTED)
async def new_password(schema: NewPasswordSchema):
    if auth(schema.user_name, schema.token):
        this_user: sn.User = users[schema.user_name]
        this_user.change_password(schema.new_password)
        return {"data": "Password changed successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to change the password")


@app.post("/signout", status_code=status.HTTP_200_OK)
async def signout(credentials: SessionSchema):
    if auth(credentials.user_name, credentials.token):
        sessions.pop(credentials.user_name)
        return {"data": "signed out"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=not_authorized)


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def post(post: PostSchema):
    if auth(post.user_name, post.token):
        this_user: sn.User = users[post.user_name]
        return {"data": this_user.post(post.content)}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to post")

@app.get("/users/{user_name}/{post_id}", status_code=status.HTTP_200_OK)
async def get_post(user_name: str, post_id: int):
    if user_name in users:
        this_user: sn.User = users[user_name]
        if post_id in this_user.posts:
            return {"data": this_user.posts[post_id]}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The post you are looking for does not exist")


@app.delete("/users/{user_name}/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(session: SessionSchema, user_name: str, post_id: int):
    if auth(session.user_name, session.token):
        this_user: sn.User = users[session.user_name]
        this_user.delete_post(post_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=not_authorized)


@app.get("/users/{user_name}")
async def get_user(user_name: str):
    if user_name in users:
        this_user: sn.User = users[user_name]
        return {"data": {"user_name": this_user.user_name, "posts": this_user.posts}}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The user {user_name} does not exist")


@app.post("/users/{user_name}", status_code=status.HTTP_202_ACCEPTED)
async def follow_user(session: SessionSchema, user_name: str):
    if auth(session.user_name, session.token):
        if user_name not in users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        follower: sn.User = users[session.user_name]
        follower.follow(user_name)
        return {"data": "Followed"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=not_authorized)


@app.post("/unfollow/{user_name}", status_code=status.HTTP_202_ACCEPTED)
async def unfollow_user(session: SessionSchema, user_name: str):
    if auth(session.user_name, session.token):
        follower: sn.User = users[session.user_name]
        if user_name not in follower.following:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        follower.unfollow(user_name)
        return {"data": "Unfollowed"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=not_authorized)
    

@app.post("/feed")
async def get_feed(session: SessionSchema):
    if auth(session.user_name, session.token):
        this_user: sn.User = users[session.user_name]
        filtered_user_posts = [user.posts for username, user in users.items() if username in this_user.following]
        feed_posts = []
        for posts_dict in filtered_user_posts:
            feed_posts.extend(posts_dict.values())
        return {"data": feed_posts}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
