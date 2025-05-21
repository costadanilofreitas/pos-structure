import _ from 'lodash'

export function checkIfHasActiveSaleLine(order) {
  let hasActiveSaleLine = false
  _.forEach(order.SaleLine, (saleLine) => {
    if (saleLine.level === '0' && saleLine.qty !== '0') {
      hasActiveSaleLine = true
      return false
    }
    return true
  })
  return hasActiveSaleLine
}
