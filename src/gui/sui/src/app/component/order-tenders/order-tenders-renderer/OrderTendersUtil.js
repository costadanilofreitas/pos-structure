export function isTefPaymentType(tenderType) {
  return tenderType.id === 1 || tenderType.id === 2
}
