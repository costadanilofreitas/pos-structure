import { ensureArray } from '3s-posui/utils'

export function createLineId(item) {
  const level = parseFloat(item.attrs.pos_level)
  return `${item.attrs.line_number}-${item.attrs.item_id}-${level}-${item.attrs.part_code}`
}

function isItemReadyStartCooking(item) {
  return item.attrs.wait_time === undefined || parseFloat(item.attrs.wait_time) <= 0
}

function itemIsNotBeingCookedNorCooked(item) {
  return item.tags.indexOf('doing') < 0 && item.tags.indexOf('done')
}

function itemIsBeingCooked(item) {
  return item.tags.indexOf('doing') >= 0
}

function iterateOnItem(item, getProductProperty) {
  if (item.attrs.item_type === 'COMBO' || item.attrs.item_type === 'OPTION') {
    const ret = []
    item.items.forEach(son => {
      const sonDataList = iterateOnItem(son, getProductProperty)
      if (sonDataList !== null) {
        if (Array.isArray(sonDataList)) {
          sonDataList.forEach(sonData => ret.push(sonData))
        } else {
          ret.push(sonDataList)
        }
      }
    })
    return ret
  }
  const productData = getProductProperty(item)
  if (productData === null) {
    return []
  }
  return ensureArray(productData)
}

export function getReadyToMakeItems(item) {
  return iterateOnItem(item, function (product) {
    if (isItemReadyStartCooking(product) && itemIsNotBeingCookedNorCooked(product)) {
      return createLineId(product)
    }
    return null
  })
}

export function getDoingItems(item) {
  return iterateOnItem(item, function (product) {
    if (itemIsBeingCooked(product)) {
      return createLineId(product)
    }
    return null
  })
}

export function getCurrentOrders(orders) {
  const currentOrders = [...orders]
  const filteredOrders = []

  for (let i = 0; i < currentOrders.length; i++) {
    if (filteredOrders.findIndex(x => x.attrs.order_id === currentOrders[i].attrs.order_id) === -1) {
      filteredOrders.push(currentOrders[i])
    }
  }

  return filteredOrders
}
