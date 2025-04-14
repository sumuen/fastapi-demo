#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.demo.crud.product import ProductDao
from backend.app.demo.model.product import Product
from backend.app.demo.schema.product import ProductCreate, ProductSchema, ProductUpdate
from backend.common.response.response_code import CustomResponseCode
from backend.common.response.response_schema import response_base
from backend.database.db import get_db

router = APIRouter()


@router.get("", response_model=None)
async def get_products(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    is_active: Optional[bool] = Query(None, description="是否上架")
) -> dict:
    """
    获取产品列表
    """
    products = await ProductDao.get_multi(db=db, skip=skip, limit=limit, is_active=is_active)
    return response_base.success(data=[ProductSchema.model_validate(product) for product in products])


@router.get("/{product_id}", response_model=None)
async def get_product(
    product_id: int = Path(..., gt=0, description="产品ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取产品详情
    """
    product = await ProductDao.get(db=db, product_id=product_id)
    if not product:
        return response_base.fail(res=CustomResponseCode.HTTP_404, data={"msg": "产品不存在"})
    return response_base.success(data=ProductSchema.model_validate(product))


@router.post("", response_model=None)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    创建产品
    """
    # 检查是否存在同名产品
    product = await ProductDao.get_by_name(db=db, name=product_in.name)
    if product:
        return response_base.fail(
            res=CustomResponseCode.HTTP_400, 
            data={"msg": f"产品 '{product_in.name}' 已存在"}
        )
    
    # 创建产品
    product = await ProductDao.create(db=db, obj_in=product_in)
    await db.commit()
    
    return response_base.success(
        res=CustomResponseCode.HTTP_201,
        data=ProductSchema.model_validate(product)
    )


@router.put("/{product_id}", response_model=None)
async def update_product(
    product_in: ProductUpdate,
    product_id: int = Path(..., gt=0, description="产品ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    更新产品
    """
    # 获取产品
    product = await ProductDao.get(db=db, product_id=product_id)
    if not product:
        return response_base.fail(
            res=CustomResponseCode.HTTP_404, 
            data={"msg": "产品不存在"}
        )
    
    # 检查产品名称是否重复
    if product_in.name and product_in.name != product.name:
        existing_product = await ProductDao.get_by_name(db=db, name=product_in.name)
        if existing_product:
            return response_base.fail(
                res=CustomResponseCode.HTTP_400, 
                data={"msg": f"产品 '{product_in.name}' 已存在"}
            )
    
    # 更新产品
    product = await ProductDao.update(db=db, db_obj=product, obj_in=product_in)
    await db.commit()
    
    return response_base.success(data=ProductSchema.model_validate(product))


@router.delete("/{product_id}", response_model=None)
async def delete_product(
    product_id: int = Path(..., gt=0, description="产品ID"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    删除产品
    """
    # 获取产品
    product = await ProductDao.get(db=db, product_id=product_id)
    if not product:
        return response_base.fail(
            res=CustomResponseCode.HTTP_404, 
            data={"msg": "产品不存在"}
        )
    
    # 删除产品
    result = await ProductDao.remove(db=db, product_id=product_id)
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