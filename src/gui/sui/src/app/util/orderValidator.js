export function orderHasAttribute(order, attrName) {
  const notValid = order == null || order['@attributes'] == null

  if (notValid) {
    return false
  }

  if (attrName != null) {
    return order['@attributes'][attrName] != null
  }

  return true
}

export function orderInState(order, ...states) {
  const notValid = order == null || order['@attributes'] == null

  if (notValid) {
    return false
  }

  return states.some(state => {
    return order['@attributes'].state === state
  })
}

export function orderNotInState(order, ...states) {
  const notValid = order == null || order['@attributes'] == null

  if (notValid) {
    return true
  }

  return states.every(state => {
    return order['@attributes'].state !== state
  })
}

export function orderHasProperty(order, propertyName) {
  const notValid = order == null

  if (notValid) {
    return false
  }

  if (propertyName != null) {
    return order[propertyName] != null
  }

  return true
}
