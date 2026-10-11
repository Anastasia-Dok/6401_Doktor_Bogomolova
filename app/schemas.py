from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


# ============ ROLE ============
class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: int
    name: str


# ============ USER ============
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: str) -> str:
        v = v.strip()
        if " " in v:
            raise ValueError("Username не может содержать пробелы")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if v.isalpha():
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if v.isdigit():
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        return v
    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower()


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str) -> str:
        return v.lower()


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    username: str
    email: EmailStr
    role: RoleOut


class UserLogin(BaseModel):
    login: str          # username или email
    password: str


# ============ LIST ============
class ListCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    list_id: int
    title: str


# ============ NOTE ============
class NoteCreate(BaseModel):
    list_id: int
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    review: str | None = None
    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Значение не может быть пустым")
        return v


class NoteUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    review: str | None = None
    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Значение не может быть пустым")
        return v

class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    note_id: int
    user_id: int
    list_id: int
    title: str
    author: str
    review: str | None


# ============ SUBSCRIPTION ============
class SubscriptionCreate(BaseModel):
    list_id: int


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    list_id: int

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"