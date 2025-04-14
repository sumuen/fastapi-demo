#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Union

from sqlalchemy import String, Float, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.common.model import Base, id_key
from backend.database.db import uuid4_str
from backend.utils.timezone import timezone


class Order(Base):
    """订单表"""

    __tablename__ = 'demo_order'

    id: Mapped[id_key] = mapped_column(init=False)
    order_number: Mapped[str] = mapped_column(String(50), init=False, default_factory=uuid4_str, unique=True, comment='订单编号')
    total_amount: Mapped[float] = mapped_column(Float, default=0.0, comment='订单总金额')
    status: Mapped[int] = mapped_column(Integer, default=0, comment='订单状态(0待付款 1已付款 2已发货 3已完成 4已取消)')
    address: Mapped[str | None] = mapped_column(String(255), default=None, comment='收货地址')
    contact_name: Mapped[str | None] = mapped_column(String(50), default=None, comment='联系人')
    contact_phone: Mapped[str | None] = mapped_column(String(20), default=None, comment='联系电话')
    remarks: Mapped[str | None] = mapped_column(String(500), default=None, comment='订单备注')
    
    # 用户订单关联(这里假设有user_id，如果项目中已有用户表，可以关联到该表)
    user_id: Mapped[int | None] = mapped_column(Integer, default=None, comment='用户ID')
    
    # 订单项关联
    order_items: Mapped[list['OrderItem']] = relationship(init=False, back_populates='order')


class OrderItem(Base):
    """订单项表"""

    __tablename__ = 'demo_order_item'

    id: Mapped[id_key] = mapped_column(init=False)
    # 订单关联 
    order_id: Mapped[int] = mapped_column(ForeignKey('demo_order.id', ondelete='CASCADE'), comment='订单ID')
    # 产品关联
    product_id: Mapped[int | None] = mapped_column(ForeignKey('demo_product.id', ondelete='SET NULL'), comment='产品ID')
    # 以下字段有默认值，放在没有默认值的字段之后
    quantity: Mapped[int] = mapped_column(Integer, default=1, comment='购买数量')
    unit_price: Mapped[float] = mapped_column(Float, default=0.0, comment='单价')
    total_price: Mapped[float] = mapped_column(Float, default=0.0, comment='总价')
    
    # 关系定义
    order: Mapped[Union['Order', None]] = relationship(init=False, back_populates='order_items')
    product: Mapped[Union['Product', None]] = relationship(init=False)  # noqa: F821 