#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional, List

from pydantic import Field

from backend.common.schema import SchemaBase


class OrderItemBase(SchemaBase):
    """订单项基础模型"""
    product_id: int = Field(..., description="产品ID")
    quantity: int = Field(1, ge=1, description="购买数量")
    unit_price: float = Field(..., ge=0, description="单价")


class OrderItemCreate(OrderItemBase):
    """订单项创建模型"""
    pass


class OrderItemUpdate(OrderItemBase):
    """订单项更新模型"""
    quantity: Optional[int] = Field(None, ge=1, description="购买数量")


class OrderItemSchema(OrderItemBase):
    """订单项查询模型"""
    id: int
    order_id: int
    total_price: float
    created_time: datetime
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderBase(SchemaBase):
    """订单基础模型"""
    address: Optional[str] = Field(None, description="收货地址")
    contact_name: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    remarks: Optional[str] = Field(None, description="订单备注")
    user_id: Optional[int] = Field(None, description="用户ID")


class OrderCreate(OrderBase):
    """订单创建模型"""
    items: List[OrderItemCreate] = Field(..., description="订单项列表")


class OrderUpdate(OrderBase):
    """订单更新模型"""
    status: Optional[int] = Field(None, ge=0, le=4, description="订单状态(0待付款 1已付款 2已发货 3已完成 4已取消)")
    address: Optional[str] = Field(None, description="收货地址")
    contact_name: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    remarks: Optional[str] = Field(None, description="订单备注")


class OrderSchema(OrderBase):
    """订单查询模型"""
    id: int
    order_number: str
    total_amount: float
    status: int
    created_time: datetime
    updated_time: Optional[datetime] = None
    order_items: List[OrderItemSchema] = []

    class Config:
        from_attributes = True 