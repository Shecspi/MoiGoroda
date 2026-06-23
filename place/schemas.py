# ---------------------------------------------
#
# Copyright © Egor Vavilov (Shecspi)
# Licensed under the Apache License, Version 2.0
#
# ----------------------------------------------

from __future__ import annotations

import msgspec


class TagOSMItem(msgspec.Struct):
    id: int
    name: str


class CategoryItem(msgspec.Struct):
    id: int
    name: str
    tags_detail: list[TagOSMItem]


class PlaceCollectionItem(msgspec.Struct):
    id: str
    title: str
    is_public: bool
    user: int


class PlaceItem(msgspec.Struct):
    id: int
    name: str
    latitude: float
    longitude: float
    category_detail: CategoryItem
    created_at: str
    updated_at: str
    is_visited: bool
    collection_detail: PlaceCollectionItem | None
