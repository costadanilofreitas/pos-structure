export default class ItemsServedCommandProcessor {
  constructor(msgBus) {
    this.msgBus = msgBus
  }

  handleCommand(orderId, view) {
    this.msgBus.sendKDSSetState(orderId, 'ITEMS_SERVED', view)
  }
}
