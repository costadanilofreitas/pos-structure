export const EDITING_ITEM = 'EDITING_ITEM'
export const CANCELING_EDITING_ITEM = 'CANCELING_EDITING_ITEM'
export const CHANGE_PRICE_ITEM = 'CHANGE_PRICE_ITEM'

export function editingItem(partCode, comboPartCode) {
  return {
    type: EDITING_ITEM,
    partCode: partCode,
    comboPartCode: comboPartCode
  }
}

export function cancelEditingItem(partCode, comboPartCode) {
  return {
    type: CANCELING_EDITING_ITEM,
    partCode: partCode,
    comboPartCode: comboPartCode
  }
}

export function changePriceItem(partCode, comboPartCode, price) {
  return {
    type: CHANGE_PRICE_ITEM,
    partCode: partCode,
    comboPartCode: comboPartCode,
    price: price
  }
}
