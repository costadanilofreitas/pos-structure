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

export function getNotDoneLowestSendMoment(items) {
  let lowestSendMoment = null

  items.forEach(item => {
    if (item.sendMoment != null && !item.wontMake() && !item.isDone()) {
      if (lowestSendMoment == null || lowestSendMoment > item.sendMoment) {
        lowestSendMoment = item.sendMoment
      }
    }
  })

  return lowestSendMoment
}

export function isAllDone(items) {
  const subItemStatus = items.map(x => x.isDone() || x.wontMake())

  for (let i = 0; i < subItemStatus.length; i++) {
    if (!subItemStatus[i] && items[i] != null && !items[i].isIngredient(items[i])) {
      const item = items[i]
      if (item.itemHasNoQuantityAndDontReachedSendMoment(item) || item.itemIsVoidedAndDontReachedSendMoment(item)) {
        subItemStatus[i] = true
      }
    }
  }

  return subItemStatus.every(item => item)
}

export function isAllWaiting(items) {
  const subItemStatus = items.filter(item => {
    return item.isWaiting() || item.isDone() || item.wontMake()
  })

  return subItemStatus.every(item => item)
}

export function getMostRecentDoing(items) {
  let mostRecentDoing = null

  let values = items.map(item => {
    if (item.isBeingCooked() && !item.wontMake()) {
      let found = false
      for (let i = item.tagHistory.length - 1; i >= 0; i--) {
        const event = item.tagHistory[i]
        if (event.tag === 'doing' && event.action === 'added') {
          if (mostRecentDoing == null || mostRecentDoing > new Date(event.timestamp)) {
            mostRecentDoing = new Date(event.timestamp)
            found = true
            break
          }
        }
        if (event.tag === 'doing' && event.action === 'removed') {
          break
        }
      }

      if (!found) {
        for (let i = item.tagHistory.length - 1; i >= 0; i--) {
          const event = item.tagHistory[i]
          if (event.tag === 'done' && event.action === 'added') {
            if (mostRecentDoing == null || mostRecentDoing > event.timestamp) {
              mostRecentDoing = event.timestamp
              break
            }
          }
        }
      }
      return mostRecentDoing
    }
    return null
  })
  values = values.filter(x => x !== null)
  if (values.length > 0) {
    return values[values.length - 1]
  }
  return null
}

function getTimeByTagAndAction(items, tag, action) {
  let values = items.map(item => {
    for (let i = 0; i < item.tagHistory.length; i++) {
      const event = item.tagHistory[i]
      if (event.tag === tag && event.action === action) {
        return new Date(event.timestamp)
      }
    }
    return null
  })
  values = values.filter(x => x !== null)
  if (values.length > 0) {
    return values[0]
  }
  return null
}

export function getDoingTime(items) {
  return getTimeByTagAndAction(items, 'doing', 'added')
}

export function firstItemIsDoingOrDone(items) {
  return items.length > 0 && items[0].isDoingOrDone()
}

export function firstItemIsDone(items) {
  return items.length > 0 && items[0].isDone()
}
