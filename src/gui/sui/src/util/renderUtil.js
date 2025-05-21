export function ensureArray(children) {
  let childArray = children
  if (!Array.isArray(childArray)) {
    childArray = [children]
  }
  return childArray
}

export function findChildByType(children, type, origin) {
  let ret = null
  ensureArray(children).some(child => {
    if (child == null) {
      return false
    }

    if (child.type === type) {
      ret = child
      return true
    }

    if (child.props.children == null) {
      return false
    }

    ensureArray(child.props.children).some(grandChild => {
      ret = findChildByType(grandChild, type, origin != null ? origin : child)
      return ret != null
    })
    return ret != null
  })

  return ret
}
export function shallowIgnoreEquals(obj1, obj2, ...ignoredProps) {
  return !Object.keys(obj1).some(key => {
    if (ignoredProps.indexOf(key) >= 0) {
      return false
    }

    return obj1[key] !== obj2[key]
  })
}

export function shallowCompareEquals(obj1, obj2, ...compareProps) {
  return !Object.keys(obj1).some(key => {
    if (compareProps.indexOf(key) >= 0) {
      return obj1[key] !== obj2[key]
    }
    return false
  })
}

export function deepEquals(obj1, obj2, ...ignoredProps) {
  return !Object.keys(obj1).some(key => {
    if (ignoredProps.indexOf(key) >= 0) {
      return false
    }

    return !_.isEqual(obj1[key], obj2[key])
  })
}
