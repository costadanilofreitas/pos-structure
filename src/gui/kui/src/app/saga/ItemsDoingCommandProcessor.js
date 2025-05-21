import { parseISO8601Date } from '3s-posui/utils'


export default class ItemsDoingCommandProcessor {
  constructor(msgBus) {
    this.msgBus = msgBus
  }

  toggleDoingItems(line, timeDelta, view) {
    const doingItems = this.getDoingItems(line)
    const dateNow = new Date()
    const validDoingItems = []
    doingItems.forEach(item => {
      const itemDate = item.getLastDoing()
      const diff = (dateNow - parseISO8601Date(itemDate)) + timeDelta
      if (diff < 15000) {
        validDoingItems.push(item.getLineId())
      }
    })

    if (validDoingItems.length > 0) {
      const orderId = line.orderData.attributes.id
      this.sendToKds(orderId, validDoingItems, view)
    }
  }

  toggleReadyItems(line, timeDelta, view) {
    const readyToMakeItems = this.getReadyToMakeItems(line, timeDelta)

    if (readyToMakeItems.length > 0) {
      const orderId = line.orderData.attributes.id
      this.sendToKds(orderId, readyToMakeItems, view)
    }
  }

  toggleWaitingItems(line, timeDelta, view) {
    const notDoneItems = this.getWaitingItems(line)
    if (notDoneItems.length > 0) {
      const orderId = line.orderData.attributes.id
      this.sendToKds(orderId, notDoneItems, view)
    }
  }


  handleCommand(line, timeDelta, view) {
    this.toggleDoingItems(line, timeDelta, view)
    this.toggleReadyItems(line, timeDelta, view)
    this.toggleWaitingItems(line, timeDelta, view)
  }

  sendToKds(orderId, items, view) {
    const lineIds = items.join(';')
    this.msgBus.sendKDSToggleNamedTagLine(orderId, lineIds, 'doing', view)
  }

  getReadyToMakeItems(line, timeDelta) {
    const readyItems = []

    for (let i = 0; i < line.items.length; i++) {
      const item = line.items[i]
      if (item.qty > 0 && item.orderState !== 'VOIDED') {
        if (item.isReadyToStartCooking(timeDelta) &&
          item.isNotBeingCookedNorCooked() &&
          !item.wontMake()) {
          readyItems.push(item.getLineId())
        }
      }
    }

    return readyItems
  }

  getDoingItems(line) {
    const doingItems = []

    for (let i = 0; i < line.items.length; i++) {
      const item = line.items[i]
      if (item.qty > 0 && item.orderState !== 'VOIDED') {
        if (item.isBeingCooked() &&
          !item.wontMake()) {
          doingItems.push(item)
        }
      }
    }

    return doingItems
  }
  getWaitingItems(line) {
    const waitingItems = []

    for (let i = 0; i < line.items.length; i++) {
      const item = line.items[i]
      if (item.qty > 0 && item.orderState !== 'VOIDED') {
        if (item.isWaiting() && !item.wontMake() && !item.isDoingOrDone()) {
          waitingItems.push(item)
        }
      }
    }

    return waitingItems
  }
}
