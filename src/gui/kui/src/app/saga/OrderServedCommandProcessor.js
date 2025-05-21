export default class OrderServedCommandProcessor {
  constructor(msgBus) {
    this.msgBus = msgBus
  }

  handleCommand(orderId, view) {
    this.msgBus.sendKDSSetState(orderId, 'SERVED', view)
  }
}
