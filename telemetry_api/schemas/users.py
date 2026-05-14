from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """
    Базовая схема пользователя.
    """

    username: str = Field(
        ...,
        description="Уникальное имя пользователя в системе.",
        examples=["kirill"],
    )
    email: EmailStr = Field(
        ...,
        description="Email пользователя в валидном формате.",
        examples=["kirill@example.com"],
    )


class UserCreate(UserBase):
    """
    Схема создания пользователя.
    """

    pass


class UserUpdate(BaseModel):
    """
    Схема частичного обновления пользователя.
    """

    username: str | None = Field(
        default=None,
        description="Новое имя пользователя; если не передано, поле не изменяется.",
        examples=["kirill"],
    )
    email: EmailStr | None = Field(
        default=None,
        description="Новый email пользователя; если не передан, поле не изменяется.",
        examples=["kirill@example.com"],
    )


class UserRead(UserBase):
    """
    Схема ответа с данными пользователя.
    """

    id: int = Field(
        ...,
        description="Уникальный идентификатор пользователя.",
        examples=[1],
    )

    model_config = ConfigDict(from_attributes=True)
