# -*- coding: utf-8 -*-

from json import JSONEncoder

from application.compositiontree import CompositionTree, ProductNode


class CompositionTreeJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, CompositionTree):
            return {
                "product": o.product,
                "sons": o.sons
            }

        if isinstance(o, ProductNode):
            return {
                "type": o.type,
                "partCode": o.part_code,
                "name": o.name,
                "maxQty": o.max_qty,
                "minQty": o.min_qty,
                "defaultQty": o.default_qty,
                "unitPrice": o.unit_price,
                "addedUnitPrice": o.added_unit_price,
                "enabled": o.enabled,
                "currentQty": o.current_qty,
                "price": o.price
            }

        return super(CompositionTreeJsonEncoder, self).default(o)
