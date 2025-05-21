export default class OrderDeliveredCommandProcessor {
  constructor(msgBus) {
    this.msgBus = msgBus
  }

  handleCommand(orderId, view) {
    this.msgBus.sendKDSSetState(orderId, 'DELIVERED', view)
  }
}
