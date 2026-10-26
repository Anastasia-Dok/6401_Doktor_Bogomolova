from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
#какие данные клиент присылает и какие получает обратно
#Data Transfer Object

#Схема ответа — как роль уходит клиенту
class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)#читает поля из атрибутов ORM-объекта
    role_id: int
    name: str


#вход при регистрации. данные от клиента (тело запроса).
class UserCreate(BaseModel):
                        #обяз нет знач по умолч-ю
    username: str = Field(..., min_length=3, max_length=100)
    #EmailStr проверяет формат + требует email-validator
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)

    @field_validator("username")#декоратор Pydantic: привязать валидатор к полю username
    @classmethod
                        #ссылка на класс
    def username_no_spaces(cls, v: str) -> str:
        v = v.strip()#убрать пробелы по краям
        if " " in v: #если после strip() внутри остался пробел — отклонить
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
   

#вход при PATCH профиля данные от клиента (тело запроса).
class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    @field_validator("email")
    @classmethod
    def email_lower(cls, v: str | None) -> str | None:
        return v.lower() if v is not None else None

#ответ с данными пользователя
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)#Pydantic может читать из ORM-объекта.
    # данные из User
    user_id: int
    username: str
    email: EmailStr
    #вложенная схема.
    role: RoleOut



# Схема входных данных при создании списка
class ListCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)

#Ответ клиенту — list_id и title
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
    def strip_whitespace(cls, v: str | None) -> str | None:
        if v is None:
            return None
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
    access_token: str #сам JWT
    token_type: str = "bearer" #без шифрований

    # ============ ANALYTICS ============
class SummaryOut(BaseModel):
    users: int
    lists: int
    notes: int
    subscriptions: int


class TopListsOut(BaseModel):
    list_id: int
    title: str
    notes_count: int
    subscribers_count: int


class TopUsersOut(BaseModel):
    user_id: int
    username: str
    email: str
    notes_count: int


class TopAuthorsOut(BaseModel):
    author: str
    mentions: int