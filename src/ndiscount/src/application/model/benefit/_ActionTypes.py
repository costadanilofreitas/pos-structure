from enum import Enum


class ActionTypes(Enum):
    discountPercentageOnTotal = "discountPercentageOnTotal"
    discountPercentageByItems = "discountPercentageByItems"
    discountAmountOnTotal = "discountAmountOnTotal"
    discountAmountByItems = "discountAmountByItems"
    itemsToAdd = "itemsToAdd"
