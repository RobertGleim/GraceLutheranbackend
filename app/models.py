from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import Column, String, ForeignKey, DATE
from datetime import date


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(Base):
    __tablename__ = 'users'
    
    

    id: Mapped[int] = mapped_column(primary_key=True,)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(500), nullable=False)
    roles: Mapped[str] = mapped_column(String(120), nullable=False, default='user')
                                       