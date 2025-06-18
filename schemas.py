from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    active: bool = True
    admin: bool = False

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    user: int

    class Config:
        from_attributes = True