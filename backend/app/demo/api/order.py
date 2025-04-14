#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.demo.crud.order import OrderDao
from backend.app.demo.crud.product import ProductDao
from backend.app.demo.model.order import Order
from backend.app.demo.schema.order import OrderCreate, OrderSchema, OrderUpdate
from backend.common.response.response_code import CustomResponseCode
from backend.common.response.response_schema import response_base
from backend.database.db import get_db

router = APIRouter()


@router.get("", response_model=None)
async def get_orders(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    user_id: Optional[int] = Query(None, description="用户ID")
) -> dict:
    """
    获取订单列表
    """
    if user_id:
        # 根据用户ID获取订单
        orders, total = await OrderDao.get_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
        return response_base.success(data={
            "items": [OrderSchema.model_validate(order) for order in orders],
            "total": total,
            "skip": skip,
            "limit": limit
        })
    else:
        # 获取所有订单（仅用于管理员，实际场景可能需要权限验证）
        # 这里实现简单的分页
        stmt = await db.execute(f"SELECT COUNT(*) FROM demo_order")
        total = stmt.scalar()
        
        orders = []
        result = await db.execute(f"SELECT * FROM demo_order ORDER BY created_time DESC LIMIT {limit} OFFSET {skip}")
        for row in result:
            order = await OrderDao.get(db=db, order_id=row.id)
            if order:
                orders.append(order)
        
        return response_base.success(data={
            "items": [OrderSchema.model_validate(order) for order in orders],
            "total": total,
            "skip": skip,
            "limit": limit
        })


@router.get("/{order_id}", response_model=None)
async def get_order(
    order_id: int = Path(..., gt=0, description="订单ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取订单详情
    """
    order = await OrderDao.get(db=db, order_id=order_id)
    if not order:
        return response_base.fail(res=CustomResponseCode.HTTP_404, data={"msg": "订单不存在"})
    return response_base.success(data=OrderSchema.model_validate(order))


@router.post("", response_model=None)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    创建订单
    """
    # 检查产品库存是否足够
    for item in order_in.items:
        product = await ProductDao.get(db=db, product_id=item.product_id)
        if not product:
            return response_base.fail(
                res=CustomResponseCode.HTTP_400, 
                data={"msg": f"产品ID:{item.product_id} 不存在"}
            )
        if product.stock < item.quantity:
            return response_base.fail(
                res=CustomResponseCode.HTTP_400, 
                data={"msg": f"产品 '{product.name}' 库存不足，当前库存: {product.stock}"}
            )
    
    # 创建订单
    try:
        order = await OrderDao.create(db=db, obj_in=order_in)
        
        # 更新产品库存
        for item in order.order_items:
            await ProductDao.update_stock(db=db, product_id=item.product_id, quantity=item.quantity)
        
        # 提交事务
        await db.commit()
        
        return response_base.success(
            res=CustomResponseCode.HTTP_201,
            data=OrderSchema.model_validate(order)
        )
    except Exception as e:
        # 回滚事务
        await db.rollback()
        return response_base.fail(
            res=CustomResponseCode.HTTP_500, 
            data={"msg": f"创建订单失败: {str(e)}"}
        )


@router.put("/{order_id}", response_model=None)
async def update_order(
    order_in: OrderUpdate,
    order_id: int = Path(..., gt=0, description="订单ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    更新订单状态
    """
    # 获取订单
    order = await OrderDao.get(db=db, order_id=order_id)
    if not order:
        return response_base.fail(
            res=CustomResponseCode.HTTP_404, 
            data={"msg": "订单不存在"}
        )
    
    # 检查订单状态更新逻辑（实际场景可能有更复杂的状态转换验证）
    if order_in.status is not None:
        # 已取消的订单不能修改状态
        if order.status == 4:
            return response_base.fail(
                res=CustomResponseCode.HTTP_400, 
                data={"msg": "已取消的订单不能修改状态"}
            )
        # 已完成的订单不能修改为其他状态（除了取消）
        if order.status == 3 and order_in.status != 4:
            return response_base.fail(
                res=CustomResponseCode.HTTP_400, 
                data={"msg": "已完成的订单不能修改为其他状态"}
            )
    
    # 更新订单
    try:
        order = await OrderDao.update(db=db, db_obj=order, obj_in=order_in)
        await db.commit()
        return response_base.success(data=OrderSchema.model_validate(order))
    except Exception as e:
        await db.rollback()
        return response_base.fail(
            res=CustomResponseCode.HTTP_500, 
            data={"msg": f"更新订单失败: {str(e)}"}
        )


@router.delete("/{order_id}", response_model=None)
async def delete_order(
    order_id: int = Path(..., gt=0, description="订单ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    删除订单
    """
    # 获取订单
    order = await OrderDao.get(db=db, order_id=order_id)
    if not order:
        return response_base.fail(
            res=CustomResponseCode.HTTP_404, 
            data={"msg": "订单不存在"}
        )
    
    # 删除订单（实际场景可能只是标记为删除状态而不是真正删除）
    result = await OrderDao.remove(db=db, order_id=order_id)
    await db.commit()
    
    if result:
        return response_base.success(
            res=CustomResponseCode.HTTP_204,
            data=None
        )
    return response_base.fail(
        res=CustomResponseCode.HTTP_500, 
        data={"msg": "删除失败"}
    ) 