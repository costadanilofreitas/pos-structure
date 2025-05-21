const TenderType = {
  Cash: 0,
  CreditCard: 1,
  DebitCard: 2,
  ExternalPayment: 3
}

export function getTypeName(tenderType) {
  switch (tenderType) {
    case TenderType.Cash:
      return '$CASH'
    case TenderType.CreditCard:
      return '$CREDIT_CARD'
    case TenderType.DebitCard:
      return '$DEBIT_CARD'
    case TenderType.ExternalPayment:
      return '$EXTERNAL_PAYMENT'
    default:
      return `$INVALID_TENDER_TYPE_${tenderType}`
  }
}

export default Object.freeze(TenderType)
