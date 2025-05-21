import { ensureArray } from '3s-posui/utils'

export default class Item {
  constructor(
    lineNumber,
    itemId,
    partCode,
    level,
    posLevel,
    itemType,
    qty,
    defaultQty,
    multipliedQty,
    description,
    items,
    tags,
    tagHistory,
    comments,
    waitTime,
    sendMoment,
    prepTime,
    orderState,
    lastUpdated,
    voided) {
    this.lineNumber = lineNumber
    this.itemId = itemId
    this.partCode = partCode
    this.level = level
    this.posLevel = posLevel
    this.itemType = itemType
    this.qty = qty
    this.defaultQty = defaultQty
    this.multipliedQty = multipliedQty
    this.description = description
    this.items = items
    this.tags = tags
    this.tagHistory = tagHistory
    this.comments = comments
    this.waitTime = waitTime
    this.sendMoment = sendMoment
    this.prepTime = prepTime
    this.orderState = orderState
    this.lastUpdated = lastUpdated
    this.voided = voided
  }

  getItemId() {
    return this.lineNumber + '.' + this.itemId + '.' + this.level + '.' + this.partCode
  }

  getLineId() {
    return this.lineNumber + '-' + this.itemId + '-' + this.posLevel + '-' + this.partCode
  }

  isProduct() {
    return this.itemType === 'PRODUCT' || this.itemType === 'CANADD'
  }

  getItemCode() {
    return this.itemId + '.' + this.partCode
  }

  hasTags() {
    return this.tags.length > 0
  }

  doesNotHaveTags() {
    return this.tags.length === 0
  }

  getLastTag() {
    for (let i = this.tags.length - 1; i >= 0; i--) {
      if (this.tags[i] !== 'printed') {
        return this.tags[i]
      }
    }
    return null
  }

  isReadyToStartCooking(timeDelta) {
    if (this.sendMoment != null) {
      const sendDiff = (new Date() - this.sendMoment) + timeDelta
      return sendDiff >= 0 && this.isNotBeingCookedNorCooked() && !this.wontMake()
    }
    return false
  }

  isNotBeingCookedNorCooked() {
    return this.tags.indexOf('doing') < 0 && this.tags.indexOf('done') < 0
  }

  isBeingCooked() {
    return this.tags.indexOf('doing') >= 0 && this.tags.indexOf('done') < 0
  }

  isDone() {
    return this.tags.indexOf('done') >= 0
  }

  isDoingOrDone() {
    return this.tags.indexOf('done') >= 0 || this.tags.indexOf('doing') >= 0
  }

  isWaiting() {
    return this.tags.indexOf('wait-prep-time') >= 0
  }

  wontMake() {
    return this.tags.indexOf('dont-need-cook') >= 0 || this.qty === 0
  }

  isAllWontMake() {
    const subItemStatus = this.iterateOnItem(this, function (product) {
      return product.wontMake()
    })

    return subItemStatus.every(item => item)
  }

  isAllVoided() {
    const subItemStatus = this.iterateOnItem(this, function (product) {
      return product.qty === 0
    })

    return subItemStatus.every(item => item)
  }

  getLastDoing() {
    let mostRecentDoing = null
    const values = this.iterateOnItem(this, function (product) {
      if (product.isBeingCooked()) {
        for (let i = product.tagHistory.length - 1; i >= 0; i--) {
          const event = product.tagHistory[i]
          if (event.tag === 'doing') {
            if (mostRecentDoing == null || mostRecentDoing < event.timestamp) {
              mostRecentDoing = event.timestamp
              break
            }
          }
        }

        return mostRecentDoing
      }
      return null
    })

    if (values.length > 0) {
      return values[0]
    }
    return null
  }

  getHighestPrepTime() {
    let highestPrepTime = null

    this.iterateOnItem(this, function (product) {
      if (product.prepTime != null) {
        if (highestPrepTime == null && highestPrepTime < product.prepTime) {
          highestPrepTime = product.prepTime
        }
      }
    })

    return highestPrepTime
  }

  getLowestSendMoment() {
    let lowestSendMoment = null

    this.iterateOnItem(this, function (product) {
      if (product.sendMoment != null && !product.wontMake()) {
        if (lowestSendMoment == null || lowestSendMoment > product.sendMoment) {
          lowestSendMoment = product.sendMoment
        }
      }
    })

    return lowestSendMoment
  }

  getReadyToMakeItems(timeDelta) {
    if (this.qty === 0) {
      return null
    }

    return this.iterateOnItem(this, function (product) {
      if (product.isReadyToStartCooking(timeDelta) &&
          product.isNotBeingCookedNorCooked() &&
          !product.wontMake()) {
        return product.getLineId()
      }
      return null
    })
  }

  getNotDoneItems() {
    if (this.qty === 0) {
      return null
    }

    return this.iterateOnItem(this, function (product) {
      if (!product.isDone() && !product.wontMake()) {
        return product.getLineId()
      }
      return null
    })
  }

  getItems() {
    const items = this.iterateOnItem(this, function (product) {
      return product.getLineId()
    })

    return items
  }

  needCookItems() {
    const items = this.iterateOnItem(this, function (product) {
      const tagHistoryLength = product.tagHistory != null ? product.tagHistory.length : 0
      if (tagHistoryLength > 0 && product.tagHistory[tagHistoryLength - 1] !== 'dont-need-cook') {
        return product.getLineId()
      }
      return null
    })

    return items
  }

  getCookingItems() {
    return this.iterateOnItem(this, function (product) {
      if (product.isBeingCooked() && !product.wontMake()) {
        return product.getLineId()
      }
      return null
    })
  }

  getReadyToCook(timeDelta) {
    return this.iterateOnItem(this, function (product) {
      if (product.isReadyToStartCooking(timeDelta)) {
        return product.getLineId()
      }
      return null
    })
  }

  getDoingItems() {
    return this.iterateOnItem(this, function (product) {
      if (product.isBeingCooked() && !product.wontMake()) {
        return product
      }
      return null
    })
  }

  getWaitingItems() {
    return this.iterateOnItem(this, function (product) {
      if (product.isWaiting() && !product.wontMake() && !product.isDoingOrDone()) {
        return product.getLineId()
      }
      return null
    })
  }

  iterateOnItem(item, getProductProperty) {
    if (item.itemType === 'COMBO' || item.itemType === 'OPTION') {
      const ret = []
      item.items.forEach(son => {
        const sonDataList = this.iterateOnItem(son, getProductProperty)
        if (sonDataList !== null) {
          if (Array.isArray(sonDataList)) {
            sonDataList.forEach(sonData => ret.push(sonData))
          } else {
            ret.push(sonDataList)
          }
        }
      })
      return ret
    }
    const productData = getProductProperty(item)
    if (productData === null) {
      return []
    }
    return ensureArray(productData)
  }

  itemHasNoQuantityAndDontReachedSendMoment(item) {
    return item.qty === 0 && (item.sendMoment == null || item.sendMoment > item.lastUpdated)
  }

  itemIsVoidedAndDontReachedSendMoment(item) {
    return item.orderState === 'VOIDED' && (item.sendMoment == null || item.sendMoment > item.lastUpdated)
  }

  isIngredient(item) {
    return item != null && item.itemType.toUpperCase() === 'INGREDIENT'
  }
}
