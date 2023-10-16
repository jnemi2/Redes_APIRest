import hashlib
import datetime

print("Social has been imported")

def hash_string(text: str):
        hash_object = hashlib.sha256()
        hash_object.update(text.encode())
        return hash_object.hexdigest()


class Post:
    def __init__(self, id: int, content: str, user: str, date: datetime.datetime = datetime.datetime.now()):
        self.id = id
        self.content = content
        self.user = user
        self.date = date


class User:
    def __init__(self, user_name: str, password: str):
        #self.id = id
        self._id_of_last_post = 0
        self.user_name = user_name
        self.password = hash_string(password)
        self.posts = dict()
        self.following = []
    
    def authenticate(self, password: str):
        return hash_string(password) == self.password
    
    def change_password(self, password: str):
        self.password = hash_string(password)
    
    def post(self, content: str):
        self._id_of_last_post += 1
        new_post = Post(self._id_of_last_post, content, self.user_name)
        self.posts[self._id_of_last_post] = new_post
        return new_post
    
    def delete_post(self, post_id: int):
        if post_id in self.posts:
            return self.posts.pop(post_id)
        else:
            return None
    
    def follow(self, user_name: str):
        if user_name not in self.following:
            self.following.append(user_name)

    def unfollow(self, user_name: str):
        if user_name in self.following:
            self.following.pop(user_name)
