export default class OrderReadyCommandProcessor {
  constructor(msgBus) {
    this.msgBus = msgBus
  }

  handleCommand(orderId, view) {
    this.msgBus.sendKDSSetState(orderId, 'READY', view)
  }
}
