#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional

from pydantic import Field

from backend.common.schema import SchemaBase


class ProductBase(SchemaBase):
    """产品基础模型"""
    name: str = Field(..., description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    price: float = Field(0.0, ge=0, description="产品价格")
    stock: int = Field(0, ge=0, description="库存数量")
    is_active: bool = Field(True, description="是否上架")
    category: Optional[str] = Field(None, description="产品类别")
    image_url: Optional[str] = Field(None, description="产品图片URL")


class ProductCreate(ProductBase):
    """产品创建模型"""
    pass


class ProductUpdate(ProductBase):
    """产品更新模型"""
    name: Optional[str] = Field(None, description="产品名称")
    price: Optional[float] = Field(None, ge=0, description="产品价格")
    stock: Optional[int] = Field(None, ge=0, description="库存数量")
    is_active: Optional[bool] = Field(None, description="是否上架")


class ProductSchema(ProductBase):
    """产品查询模型"""
    id: int
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True 