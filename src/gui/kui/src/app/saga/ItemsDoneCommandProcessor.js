export default class ItemsDoneCommandProcessor {
  constructor(msgBus) {
    this.msgBus = msgBus
  }

  handleCommand(line, timeDelta, view, tagName = 'done') {
    if (this.isAllVoided(line.items)) {
      const lineIds = this.getItemsId(line.items).join(';')
      this.msgBus.sendKDSToggleNamedTagLine(line.orderData.attributes.id, lineIds, tagName, view)
      return
    }

    const itemsToReady = this.getCookingAndReadyToCookItems(line.items)
    if (itemsToReady.length > 0) {
      const lineIds = itemsToReady.join(';')
      this.msgBus.sendKDSToggleNamedTagLine(line.orderData.attributes.id, lineIds, tagName, view)
    }
  }

  getCookingAndReadyToCookItems(items) {
    const cookingItems = []

    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.qty > 0) {
        const itemCookingOrReadyToCook = item.isBeingCooked() || item.isNotBeingCookedNorCooked()
        const itemBeingCooked = itemCookingOrReadyToCook && !item.wontMake() && !item.isWaiting()

        if (itemBeingCooked) {
          cookingItems.push(item.getLineId())
        }
      }
    }

    return cookingItems
  }

  isAllVoided(items) {
    if (items[0].orderState === 'VOIDED') {
      return true
    }

    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.qty === 0) {
        return true
      }
    }

    return false
  }

  getItemsId(items) {
    const itemsId = []

    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      itemsId.push(item.getLineId())
    }

    return itemsId
  }
}
