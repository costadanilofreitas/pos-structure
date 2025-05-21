export default class OrderInvalidCommandProcessor {
  constructor(msgBus) {
    this.msgBus = msgBus
  }

  handleCommand(orderId, view) {
    this.msgBus.sendKDSSetState(orderId, 'INVALID', view)
  }
}
