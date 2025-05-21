export default class Line {
  constructor(orderData) {
    this.orderData = orderData
    this.items = []
  }

  getLineId() {
    return this.orderData.attributes.id + '.' + this.items[0].getItemId()
  }
}
