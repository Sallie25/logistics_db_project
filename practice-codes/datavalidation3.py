from pydantic import BaseModel, ValidationError

from datetime import datetime


class User(BaseModel):
    username: str
    email: str
    age: int

    bio: str = ''
    is_active: bool = True

    full_name: str | None = None


# Creating an instance of the class
user1 = User(
    username = "Salome",
    email ="sallieakapna@gmail.com",
    age = 20
)
print(user1)




