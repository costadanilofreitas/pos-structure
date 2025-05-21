const OrderStatus = {
  InProgress: 1,
  Stored: 2,
  Totaled: 3,
  Voided: 4,
  Paid: 5,
  Recalled: 6,
  SystemVoided: 7,
  Abandoned: 8
}

export default Object.freeze(OrderStatus)
