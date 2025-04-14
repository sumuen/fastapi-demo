#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.demo.model.product import Product
from backend.app.demo.schema.product import ProductCreate, ProductUpdate


class ProductDao:
    """产品数据访问对象"""

    @classmethod
    async def create(cls, db: AsyncSession, obj_in: ProductCreate) -> Product:
        """创建产品"""
        db_obj = Product(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @classmethod
    async def get(cls, db: AsyncSession, product_id: int) -> Optional[Product]:
        """根据ID获取产品"""
        stmt = select(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_name(cls, db: AsyncSession, name: str) -> Optional[Product]:
        """根据名称获取产品"""
        stmt = select(Product).where(Product.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_multi(
        cls, db: AsyncSession, *, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> List[Product]:
        """获取多个产品"""
        stmt = select(Product)
        if is_active is not None:
            stmt = stmt.where(Product.is_active == is_active)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls, db: AsyncSession, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        """更新产品"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @classmethod
    async def remove(cls, db: AsyncSession, *, product_id: int) -> bool:
        """删除产品"""
        stmt = delete(Product).where(Product.id == product_id)
        result = await db.execute(stmt)
        return result.rowcount > 0

    @classmethod
    async def update_stock(cls, db: AsyncSession, product_id: int, quantity: int) -> bool:
        """更新库存"""
        stmt = (
            update(Product)
            .where(Product.id == product_id, Product.stock >= quantity)
            .values(stock=Product.stock - quantity)
        )
        result = await db.execute(stmt)
        return result.rowcount > 0 