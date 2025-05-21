function getItemTagSet(item, orderItems, sku) {
  const tagSet = new Set()
  const currentOrderItem = orderItems.get(sku)
  if (currentOrderItem.tags) {
    currentOrderItem.tags.forEach(tag => tagSet.add(tag))
    if (item.tags) {
      item.tags.forEach(tag => tagSet.add(tag))
    }
  }

  if (item.tags && item.tags.indexOf('done') === -1 && tagSet.has('done')) {
    tagSet.delete('done')
  }
  return tagSet
}

function getNewItem(item) {
  const newItem = {}
  Object.entries(item).forEach(([key, v]) => {
    let value = v
    if (Array.isArray(value)) {
      value = value.slice()
    } else if (value instanceof Object) {
      value = Object.assign({}, value)
    }
    newItem[key] = value
  })
  return newItem
}

function squashItems(items) {
  const itemDFS = (item, arr) => {
    arr.push(item)
    if (item.items) {
      item.items.forEach(nestedItem => itemDFS(nestedItem, arr))
    }
  }
  const getItemId = item => item.attrs ? item.attrs.part_code : 0
  const getItemTreeHashUtil = item => {
    let includedItemSKUs = [].concat(getItemId(item))
    if (item.items && item.items.length) {
      includedItemSKUs = includedItemSKUs.concat(...item.items.map(nestedItem => getItemTreeHashUtil(nestedItem)))
    }
    return includedItemSKUs
  }
  const getItemTreeHash = item => getItemTreeHashUtil(item)

  const orderItems = new Map()
  items.forEach(item => {
    const sku = getItemTreeHash(item)

    if (!orderItems.has(sku)) {
      orderItems.set(sku, getNewItem(item))
    } else {
      const shouldUpdate = Number(item.attrs.qty) > 0
      if (shouldUpdate) {
        const unitTagSet = getItemTagSet(item, orderItems, sku)
        const currentOrderItem = orderItems.get(sku)
        const tagSet = new Set(currentOrderItem.tags)
        const intersection = new Set([...tagSet].filter(tag => unitTagSet.has(tag)))

        currentOrderItem.tags = [...intersection]
        const deltaQty = Number(item.attrs.qty)
        const totalQty = Number(currentOrderItem.attrs.qty) + deltaQty
        currentOrderItem.attrs.qty = totalQty.toString()
      }
    }
  })

  const flattenedItems = []
  orderItems.forEach((item) => itemDFS(item, flattenedItems))
  return flattenedItems
}

function pageInfoInOrders(orders, flatOrder, pagesCount) {
  return orders.map((o, i) => ({ ...o,
    flattenItems: flatOrder,
    page: i + 1,
    pages: pagesCount
  }))
}

function cloneIncludingNestedReferences(obj) {
  return JSON.parse(JSON.stringify(obj))
}

function generateMultipleOrders(quantity, order) {
  return Array.from({ length: quantity })
    .map(() => cloneIncludingNestedReferences(order))
}

function getOrders(order, maxItemsPerOrder, showItems, displayMode) {
  const flattenItems = squashItems(order.items)
  const pagesCount = showItems ? Math.ceil(flattenItems.length / maxItemsPerOrder) : 1
  const orders = displayMode.toLowerCase() === 'expo' ? generateMultipleOrders(pagesCount, order) : [order]
  return pageInfoInOrders(orders, flattenItems, pagesCount)
}

function isItemVoided(item) {
  return item && item.attrs && (item.attrs.qty === '0' || Number(item.attrs.qty) === 0)
}

export default class OrdersUpdateProcessor {
  constructor(prodOrders, kdsModel) {
    this.prodOrders = prodOrders
    this.kdsModel = kdsModel
    this.newProdOrders = []
  }

  process(prodOrder, lines) {
    let changed = false
    const showItems = this.kdsModel.showItems
    const displayMode = this.kdsModel.displayMode

    if (prodOrder == null) {
      const initialProdOrders = this.prodOrders
      const filteredProdOrdersArray = this.prodOrders.filter(order => order.page === 1)
      if (filteredProdOrdersArray != null && filteredProdOrdersArray.length > 0) {
        this.prodOrders = [].concat(
          ...filteredProdOrdersArray.map(order => getOrders(order, lines, showItems, displayMode))
        )
        changed = initialProdOrders.length !== this.prodOrders.length
      }
    } else if (prodOrder.items.every(item => isItemVoided(item))) {
      this.prodOrders = this.prodOrders.filter(order => order.attrs.order_id !== prodOrder.attrs.order_id)
      changed = true
    } else {
      const newProdOrdersArray = getOrders(prodOrder, lines, showItems, displayMode)
      const prodOrdersIds = new Set()

      newProdOrdersArray.forEach(order => prodOrdersIds.add(order.attrs.order_id))

      const unchangedOrders = this.prodOrders.filter(order => !prodOrdersIds.has(order.attrs.order_id))
      this.prodOrders = newProdOrdersArray.concat(unchangedOrders)

      changed = true
    }
    this.newProdOrders = this.prodOrders.sort((a, b) => a.attrs.prod_sequence.localeCompare(b.attrs.prod_sequence))
    return changed
  }
}
