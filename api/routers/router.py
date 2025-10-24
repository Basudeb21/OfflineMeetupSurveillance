from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import Product
from schemas.schema import ProductCreate, ProductUpdate

router = APIRouter()

# @router.post("/@{username}/create")

# @router.put("/@{username}/update")