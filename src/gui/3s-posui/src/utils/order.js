import _ from 'lodash'

export function isLastOption(saleLines, selectedLine) {
  let found = false
  const currentLines = _.filter(saleLines || [], (line) => {
    const saleLine = (line || {})['@attributes'] || {}
    if (found) {
      return saleLine.lineNumber === selectedLine.lineNumber
    } else if (saleLine.itemId === selectedLine.itemId &&
               saleLine.itemType === selectedLine.itemType &&
               saleLine.level === selectedLine.level &&
               saleLine.lineNumber === selectedLine.lineNumber &&
               saleLine.partCode === selectedLine.partCode) {
      found = true
    }
    return false
  })
  const hasMoreOptions = _.some(currentLines, (line) => {
    const saleLine = (line || {})['@attributes'] || {}
    return saleLine.itemType === 'OPTION'
  })
  return !hasMoreOptions
}

export function getNextOpenOption(saleLines, selectedLine, anyOption) {
  let found = false
  const addLineIfVoided = (saleLine, voidLines) => {
    const qty = parseInt(saleLine.qty, 10)
    const level = parseInt(saleLine.level, 10)
    if (level === 0 && qty === 0) {
      voidLines.push(saleLine.lineNumber)
    }
  }
  const voidedLines = []
  const currentLines = _.filter(saleLines || [], (line) => {
    const saleLine = (line || {})['@attributes'] || {}
    if (found) {
      return saleLine.lineNumber === selectedLine.lineNumber
    } else if (saleLine.itemId === selectedLine.itemId &&
               saleLine.itemType === selectedLine.itemType &&
               saleLine.level === selectedLine.level &&
               saleLine.lineNumber === selectedLine.lineNumber &&
               saleLine.partCode === selectedLine.partCode) {
      found = true
      addLineIfVoided(saleLine, voidedLines)
    }
    return false
  })
  let openOption = null
  _.some(currentLines, (line) => {
    const saleLine = (line || {})['@attributes'] || {}
    const option = saleLine.itemType === 'OPTION'
    const qty = parseInt(saleLine.qty, 10)
    const chosenQty = parseInt(saleLine.chosenQty, 10) || 0
    const maxQty = parseInt(saleLine.maxQty, 10)
    const open = (chosenQty < qty) || (anyOption && (maxQty > qty))
    addLineIfVoided(saleLine, voidedLines)
    if (option && open && !_.includes(voidedLines, saleLine.lineNumber)) {
      openOption = saleLine
      return true
    }
    return false
  })
  return openOption
}

function getOpenOption(saleLines, lineNumber, anyOption) {
  const len = (saleLines || []).length
  for (let i = 0; i < len; i++) {
    const saleLine = (saleLines[i] || {})['@attributes'] || {}
    if (parseInt(saleLine.level, 10) === 0 &&
        saleLine.lineNumber === lineNumber) {
      return getNextOpenOption(saleLines, saleLine, anyOption)
    }
  }
  return null
}

export function getFirstOpenOption(saleLines, lineNumber) {
  return getOpenOption(saleLines, lineNumber, false)
}

export function getAnyOpenOption(saleLines, lineNumber) {
  return getOpenOption(saleLines, lineNumber, true)
}

export function multiplyQtys(saleLines) {
  const lines = saleLines || []
  const len = lines.length
  const stack = {}
  for (let i = 0; i < len; i++) {
    const item = (lines[i] || {})['@attributes'] || {}
    const type = item.itemType
    const level = parseInt(item.level, 10)
    let qty = parseInt(item.qty, 10)
    if (level > 0) {
      if (type !== 'INGREDIENT' && type !== 'CANADD') {
        qty *= stack[level - 1]
        item.qty = String(qty)
      }
      if (type === 'OPTION') {
        const chosenQty = stack[level - 1] * parseInt(item.chosenQty, 10)
        item.chosenQty = String(chosenQty)
        qty = stack[level - 1] // don't multiply option solutions by the option qty
      }
      if (item.itemPrice && Number(item.itemPrice)) {
        // multiply the price by the parent's qty
        item.itemPrice = String(Number(Number(item.itemPrice) * stack[level - 1]).toFixed(2))
      }
    }
    stack[level] = qty
  }
  return saleLines
}

export function sortSaleLines(saleLines) {
  if (!saleLines) {
    return []
  }
  // As an ingredient can belong to several Product or Option,
  // its priority must be set afterwards
  let parentPrio = 0
  const orderTree = []
  let orderTreeIdx = -1
  let optionsIdx = -1
  const invalid = _.some(saleLines, (saleLine, index) => {
    const lineAttr = saleLine['@attributes'] || {}
    if (lineAttr.level === '0') {
      parentPrio = lineAttr.productPriority
    }
    if (lineAttr.itemType === 'CANADD') {
      if (lineAttr.level !== '1') {
        lineAttr.productPriority = (saleLines[index - 1] || {})['@attributes'].productPriority
      } else {
        lineAttr.productPriority = (parseInt(parentPrio, 10) + 1).toString()
      }
    }
    switch (lineAttr.level) {
      case '0':
        orderTree.push({ saleLine: saleLine, options: [] })
        orderTreeIdx++
        optionsIdx = -1
        break
      case '1':
        orderTree[orderTreeIdx].options.push({
          prio: lineAttr.productPriority,
          saleLine: saleLine,
          items: []
        })
        optionsIdx++
        break
      default:
        if (optionsIdx < 0) {
          // invalid option
          return true
        }
        orderTree[orderTreeIdx].options[optionsIdx].items.push(saleLine)
    }
    return false
  })
  if (invalid) {
    // something wrong on the input, return unsorted lines
    return saleLines
  }
  // Sort order by options priorities and reconstruct saleLines list
  const orderedSaleLines = []
  let indexSaleLine = 0
  _.forEach(orderTree, (slTree, index) => {
    // Sort
    orderTree[index].options = slTree.options.sort((a, b) => a.prio - b.prio)
    // Reconstruct
    orderedSaleLines[indexSaleLine] = orderTree[index].saleLine
    indexSaleLine++
    _.forEach(orderTree[index].options, (orderedOption) => {
      orderedSaleLines[indexSaleLine] = orderedOption.saleLine
      indexSaleLine++
      _.forEach(orderedOption.items, (item) => {
        orderedSaleLines[indexSaleLine] = item
        indexSaleLine++
      })
    })
  })

  return orderedSaleLines
}

export function consolidateSaleLines(saleLines, consolidablePlus) {
  const orderTree = []
  let orderTreeIdx = -1
  let curOpt = '0'
  if (((saleLines || []).length === 0) || (!(consolidablePlus || ''))) {
    return null
  }

  const saleLineCopy = _.cloneDeep(saleLines)

  // First, transform the Order Picture in a tree to able to move/create/delete root nodes product
  // easily. Each level of order picture is a level of the tree
  _.forEach(saleLineCopy, (saleLine, index) => {
    const lineAttr = (saleLine || {})['@attributes'] || {}
    const allOptionsResolved = !(getFirstOpenOption(saleLineCopy, lineAttr.lineNumber))
    switch (lineAttr.level) {
      case '0':
        orderTree.push({
          saleLine: saleLine,
          options: new Map(),
          computed: false,
          removeit: false,
          allOptionsResolved: allOptionsResolved
        })
        orderTreeIdx++
        break
      case '1':
        curOpt = lineAttr.partCode
        orderTree[orderTreeIdx].options.set(
          curOpt, { saleLine: _.cloneDeep(saleLine), items: new Map() }
        )
        break
      default:
        orderTree[orderTreeIdx].options.get(curOpt).items.set(index, _.cloneDeep(saleLine))
    }
  })

  // Consolidate the order. We assume that modified ingredient (iem of level=3) are not consolidated
  // Consolidable products list usually come from custom model GROUPED_PRODUCTS
  const consolidatedOrder = []
  // Cross the order and for each consolidable product, find all the other similars product
  // (same partCode), for each other similar product, merge it with the current product
  // (add quantities, lineNumber and price)
  _.forEach(orderTree, (slTreeOrig, index) => {
    const slTree = slTreeOrig
    const slTreeAttr = (slTree.saleLine || {})['@attributes'] || {}
    if (slTree.computed || !slTree.allOptionsResolved || (parseInt(slTreeAttr.qty, 10) < 1)) {
      if (parseInt(slTreeAttr.qty, 10) > 0) {
        consolidatedOrder.push(slTree)
        slTree.computed = true
      }
    } else {
      slTree.computed = true
      let hasBeenConsolidated = false
      const curPartCode = slTreeAttr.partCode
      // If product is not consolidable, just go to the end and add it to the list
      if (_.includes(consolidablePlus, slTreeAttr.partCode)) {
        _.forEach(orderTree, (othersSLOrig) => {
          const othersSL = othersSLOrig
          const otherSlAttr = (othersSL.saleLine || {})['@attributes'] || {}
          if ((otherSlAttr.partCode === curPartCode) && (!othersSL.computed) &&
              (othersSL.allOptionsResolved)) {
            hasBeenConsolidated = true
            othersSL.removeit = true
            othersSL.computed = true
            slTreeAttr.qty = (parseInt(slTreeAttr.qty, 10) +
                              parseInt(otherSlAttr.qty, 10)).toString()
            slTreeAttr.lineNumber += `|${otherSlAttr.lineNumber}`
            slTreeAttr.itemPrice = (parseFloat(slTreeAttr.unitPrice) *
                                    parseInt(otherSlAttr.qty, 10)).toString()
            _.forEach(Array.from(othersSL.options), ([optionId, otherSlOption]) => {
              const origOption = slTree.options.get(optionId)
              const origOptionAttr = (origOption.saleLine || {})['@attributes'] || {}
              origOptionAttr.lineNumber = slTreeAttr.lineNumber
              const origItems = origOption.items
              _.forEach(Array.from(otherSlOption.items), ([, otherSlItem]) => {
                const otherSlItemAttr = otherSlItem['@attributes'] || {}
                const itemId = otherSlItemAttr.partCode
                const otherQty = otherSlItemAttr.qty
                if (parseInt(otherQty, 10) >= 1) {
                  let findItem = false
                  _.forEach(Array.from(origItems), ([, originItem]) => {
                    const origItemAttr = (originItem || {})['@attributes'] || {}
                    if (origItemAttr.partCode === itemId) {
                      findItem = true
                      const curQty = parseInt(origItemAttr.qty, 10)
                      origItemAttr.qty = (curQty + parseInt(otherSlItemAttr.qty, 10)).toString()
                      origItemAttr.itemPrice = (parseFloat(origItemAttr.unitPrice) *
                                                parseInt(origItemAttr.qty, 10)).toFixed(2)
                    }
                  })
                  if (!findItem) {
                    origItems.set(itemId, _.cloneDeep(otherSlItem))
                  }
                }
              })
            })
          }
        })
      }
      // For the all the options, put the lineNumber as the root consolidated parent.
      // It should appear as the concatenated lineNumbers, like 1|3|7|...
      if (hasBeenConsolidated) {
        _.forEach(Array.from(orderTree[index].options), ([, currentOption]) => {
          _.forEach(Array.from(currentOption.items), ([, currentItem]) => {
            const item = (currentItem || {})['@attributes'] || {}
            if (!_.isEmpty(item)) {
              item.lineNumber = slTreeAttr.lineNumber
            }
          })
        })
      }
      // Then in a new list, add the consolidate product and forget the others line
      consolidatedOrder.push(slTree)
    }
  })

  // Reconstruct saleLines list
  const consolidatedSaleLines = []
  const toKeep = _.filter(consolidatedOrder, (item) => !item.removeit)
  _.forEach(toKeep, (slLevel0) => {
    consolidatedSaleLines.push(slLevel0.saleLine)
    _.forEach(Array.from(slLevel0.options), ([, slLevel1]) => {
      consolidatedSaleLines.push(slLevel1.saleLine)
      _.forEach(Array.from(slLevel1.items), ([, slLevel2]) => {
        consolidatedSaleLines.push(slLevel2)
      })
    })
  })
  return consolidatedSaleLines
}

/**
 * Given a sale line, it detects if it is a modifier and tries to find and return the immediate
 * non-modifier parent.
 * If the line is not a modifier, it is returned as-is.
 */
export function findClosestParent(order, line) {
  const { lineNumber } = line
  let nextParent = line
  const lineLevel = parseInt(line.level, 10) || 0

  // don't even try to search for root or products
  if (!lineLevel || _.includes(['PRODUCT', 'OPTION'], line.itemType)) {
    return nextParent
  }

  // create an array with current lines, according to the line number
  const currentLines = _.reduce(
    order.SaleLine || [],
    (result, lineItem) => {
      const saleLine = lineItem['@attributes'] || {}
      if (saleLine.lineNumber === lineNumber) {
        result.push(saleLine)
      }
      return result
    },
    []
  )

  // the following loop will detect if selected line is a modifier, unfortunatelly we cannot
  // just check the item type, instead of that it is considered a modifier if the item is either
  // child (in terms of level) of a 'PRODUCT' or is a grandchild of an 'OPTION' type.
  let isModifier = false
  let lastOption = null
  let lastOptionChild = null
  let lastProduct = null
  _.find(currentLines, (saleLine) => {
    const qty = parseInt(saleLine.qty, 10) || 0
    const level = parseInt(saleLine.level, 10) || 0
    const isOption = saleLine.itemType === 'OPTION'
    const isProduct = saleLine.itemType === 'PRODUCT'

    // deleted item
    if (qty === 0 && level === 0) {
      return true
    }
    let isOptionGrandChild = false
    const fullCode = `${saleLine.itemId}.${saleLine.partCode}`
    if (isOption) {
      lastOption = fullCode
    } else if (saleLine.itemId === lastOption) {
      lastOptionChild = fullCode
    } else if (saleLine.itemId === lastOptionChild) {
      isOptionGrandChild = true
    }
    let isProductChild = false
    if (isProduct) {
      lastProduct = fullCode
    } else if (saleLine.itemId === lastProduct) {
      isProductChild = true
    }
    if (_.isEqual(line, saleLine)) {
      isModifier = (isProductChild || isOptionGrandChild)
      return true
    }
    return false
  })

  // if it is a modifier, find next parent line by looping backwards
  if (isModifier) {
    let found = false
    _.findLast(currentLines, (item) => {
      if (_.isEqual(item, line)) {
        found = true
      } else if (found && item.level !== line.level) {
        nextParent = item
        return true
      }
      return false
    })
  }

  return nextParent
}

export function ensureArray(obj) {
  if (Array.isArray(obj)) {
    return obj
  }
  return [obj]
}

/**
 * Helper function that takes a JSON order as converted from an XML event in the order picture
 * style, and ensures that repeated fields are returned as array.
 * It also converts order properties to objects for easy access.
 */
export function normalizeOrder(orderJson) {
  const order = orderJson || {}
  if (order.SaleLine) {
    order.SaleLine = sortSaleLines(ensureArray(order.SaleLine))
    _.forEach(order.SaleLine || [], (saleLine) => {
      const line = saleLine
      line.Comment = (line.Comment || [])
      line.Comment = ensureArray(line.Comment)
      const lineAttr = line['@attributes'] || {}
      if (lineAttr.jsonArrayTags) {
        try {
          lineAttr.jsonArrayTags = JSON.parse(lineAttr.jsonArrayTags)
        } catch (e) {
          console.error(e)
        }
      }
      if (lineAttr.customProperties) {
        try {
          lineAttr.customProperties = JSON.parse(lineAttr.customProperties)
        } catch (e) {
          console.error(e)
        }
      }
    })
  }
  if (order.TenderHistory && order.TenderHistory.Tender) {
    order.TenderHistory.Tender = ensureArray(order.TenderHistory.Tender)
  }
  // make a dictionary with custom order properties
  const customOrderProps = ensureArray(
    (order.CustomOrderProperties || {}).OrderProperty || []
  )
  const validOrderProps = _.filter(customOrderProps, (prop) => _.has(prop, '@attributes') && _.has(prop['@attributes'], 'key'))
  order.CustomOrderProperties = _.fromPairs(
    _.map(validOrderProps, (prop) =>
      [prop['@attributes'].key, prop['@attributes'].value]
    )
  )
  return order
}
