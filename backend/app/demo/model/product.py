#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class Product(Base):
    """产品表"""

    __tablename__ = 'demo_product'

    id: Mapped[id_key] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(String(100), index=True, comment='产品名称')
    description: Mapped[str | None] = mapped_column(String(500), default=None, comment='产品描述')
    price: Mapped[float] = mapped_column(Float, default=0.0, comment='产品价格')
    stock: Mapped[int] = mapped_column(Integer, default=0, comment='库存数量')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment='是否上架(0下架 1上架)')
    category: Mapped[str | None] = mapped_column(String(50), default=None, comment='产品类别')
    image_url: Mapped[str | None] = mapped_column(String(255), default=None, comment='产品图片URL') 