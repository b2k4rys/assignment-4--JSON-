from fastapi import FastAPI, Response, Form, Depends, Cookie
from attrs import define, asdict
from fastapi.security import OAuth2PasswordBearer
import jwt
import json

app = FastAPI()

def create_access_token(id: str):
  to_encode = {'user_id': id}
  encoded_jwt = jwt.encode(to_encode, 'super-secret', 'HS256')
  return encoded_jwt


@define
class User:
  id: int
  username: str
  password: str

@define
class Flower:
  id: int
  name: str
  count: int
  price: int

class UserRepository:
  def __init__(self):
    self.users = []
  
  def save(self, user: User):
    user.id = len(self.users) + 1
    self.users.append(user)

  def get_one(self, username: str):
    for user in self.users:
      if user.username == username:
        return user
    return None
  
  def get_all(self):
    return self.users

class FlowerRepositroy:
  def __init__(self):
    self.flowers = []

  def get_all(self):
    return self.flowers
  
  def save(self, flower: Flower):
    flower.id = len(self.flowers) + 1
    self.flowers.append(flower)
  

  

 

repo = UserRepository()
repo_flowers = FlowerRepositroy()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


print(repo.get_all())

@app.post('/signup')
async def register(username: str, password: str):
  usr = User(id = 0, username=username, password=password)
  repo.save(usr)
  return usr.username


@app.get('/get_all')
async def get_all():
  users = repo.get_all()
  result = []

  for user in users:
    dict_user = asdict(user)
    result.append(dict_user)
  return result


@app.post('/login')
async def login(username:str = Form(), password: str = Form()):
  tmp = repo.get_one(username=username)
  if tmp.password == password:
    token = create_access_token(username)
    return {'access_token': token}


@app.get('/profile')
async def get_info(username: str, token: str = Depends(oauth2_scheme)):
  temp = repo.get_one(username=username)
  return {'user_name': temp.username, 'id': temp.id}

  

@app.get('/flowers')
async def get_flowers():
  result = []
  flowers = repo_flowers.get_all()

  for flower in flowers:
    temp = asdict(flower)
    result.append(temp)
  return result

  
@app.post('/add_flower')
async def add_flower(name: str, count: int, price: int):
  flw = Flower(id = 0, name=name , count=count, price=price)
  repo_flowers.save(flw)
  return flw.id

@app.post('/cart/items')
async def add_flower(response: Response, flower_id: int = Form(), items: str = Cookie(default='[]'), price: int = Cookie(default=0)):
  items_json = json.loads(items)
  flowers = repo_flowers.get_all()


  if flower_id > 0:
    items_json.append(asdict(flowers[flower_id-1]))
    price += asdict(flowers[flower_id-1])['price']
    new_items = json.dumps(items_json)
    response.set_cookie(key='items', value=new_items)
    response.set_cookie(key='price', value=price)
  return response.status_code

@app.get('/cart/items')
async def get_cart(response: Response, items: str = Cookie(default='[]'), price: int = Cookie(default=0)):
  items_json = json.loads(items)

  return {
    'items': items_json,
    'price': price
  }


@app.delete('/cart/delete_items')
async def delete_items(response: Response):
  response.delete_cookie(key='items')
  return response.status_code