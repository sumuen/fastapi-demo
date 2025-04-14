#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional, Tuple

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.demo.model.order import Order, OrderItem
from backend.app.demo.schema.order import OrderCreate, OrderUpdate, OrderItemCreate


class OrderItemDao:
    """订单项数据访问对象"""

    @classmethod
    async def create(cls, db: AsyncSession, obj_in: OrderItemCreate, order_id: int) -> OrderItem:
        """创建订单项"""
        # 计算总价
        total_price = obj_in.quantity * obj_in.unit_price
        # 创建订单项
        db_obj = OrderItem(
            order_id=order_id,
            product_id=obj_in.product_id,
            quantity=obj_in.quantity,
            unit_price=obj_in.unit_price,
            total_price=total_price,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @classmethod
    async def get_by_order(cls, db: AsyncSession, order_id: int) -> List[OrderItem]:
        """获取订单的所有订单项"""
        stmt = select(OrderItem).where(OrderItem.order_id == order_id)
        result = await db.execute(stmt)
        return result.scalars().all()


class OrderDao:
    """订单数据访问对象"""

    @classmethod
    async def create(cls, db: AsyncSession, obj_in: OrderCreate) -> Order:
        """创建订单"""
        # 创建订单
        db_obj = Order(
            address=obj_in.address,
            contact_name=obj_in.contact_name,
            contact_phone=obj_in.contact_phone,
            remarks=obj_in.remarks,
            user_id=obj_in.user_id,
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        
        # 创建订单项
        total_amount = 0
        for item in obj_in.items:
            order_item = await OrderItemDao.create(db, item, db_obj.id)
            total_amount += order_item.total_price
        
        # 更新订单总金额
        db_obj.total_amount = total_amount
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        
        return db_obj

    @classmethod
    async def get(cls, db: AsyncSession, order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.order_items))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_order_number(cls, db: AsyncSession, order_number: str) -> Optional[Order]:
        """根据订单编号获取订单"""
        stmt = select(Order).where(Order.order_number == order_number).options(selectinload(Order.order_items))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_user(
        cls, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[Order], int]:
        """获取用户的所有订单"""
        # 获取订单总数
        count_stmt = select(Order).where(Order.user_id == user_id)
        count_result = await db.execute(count_stmt)
        total = len(count_result.all())
        
        # 获取分页订单列表
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.order_items))
            .order_by(Order.created_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all(), total

    @classmethod
    async def update(cls, db: AsyncSession, *, db_obj: Order, obj_in: OrderUpdate) -> Order:
        """更新订单"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    @classmethod
    async def remove(cls, db: AsyncSession, *, order_id: int) -> bool:
        """删除订单"""
        stmt = delete(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        return result.rowcount > 0 