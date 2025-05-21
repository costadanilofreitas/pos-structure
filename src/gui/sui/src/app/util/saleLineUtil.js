import { ensureArray } from '../../util/renderUtil'

function getAttribute(saleLine, attr) {
  if (saleLine['@attributes']) {
    return saleLine['@attributes'][attr]
  }
  return saleLine[attr]
}

function getLineNumber(saleLine) {
  return getAttribute(saleLine, 'lineNumber')
}

function getLevel(saleLine) {
  return getAttribute(saleLine, 'level')
}

export function findSelectedParent(order, selectedLine) {
  return ensureArray(order.SaleLine || []).find(saleLine => {
    return getLevel(saleLine) === '0' && getLineNumber(saleLine) === getLineNumber(selectedLine)
  })
}

export function findSelectedFather(order, selectedLine) {
  return ensureArray(order.SaleLine || []).find(saleLine => {
    const fatherLevel = getLevel(selectedLine) !== '0' ? parseFloat(getLevel(selectedLine)) - 1 : 0
    const fatherCode = `${getAttribute(saleLine, 'itemId')}.${getAttribute(saleLine, 'partCode')}`
    return parseFloat(getLevel(saleLine)) === fatherLevel
      && getLineNumber(saleLine) === getLineNumber(selectedLine)
      && getAttribute(selectedLine, 'itemId') === fatherCode
  })
}

export function findSelectedLine(order, selectedLine) {
  let currentSelectedLine = selectedLine
  if (currentSelectedLine == null) {
    if (order != null && order.state === 'IN_PROGRESS' && order.SaleLine != null && order.SaleLine.length > 0) {
      for (let i = order.SaleLine.length - 1; i >= 0; i--) {
        if (parseInt(order.SaleLine[i].level, 10) === 0 && parseFloat(order.SaleLine[i].qty) > 0) {
          currentSelectedLine = order.SaleLine[i]
          break
        }
      }
    } else {
      return null
    }
  }
  let newSelectedLine = currentSelectedLine
  for (let i = 0; i < (order.SaleLine || {}).length; i++) {
    const saleLine = (order.SaleLine[i] || {})['@attributes'] || {}
    saleLine.Comment = order.SaleLine[i].Comment
    if (currentSelectedLine != null &&
      saleLine.itemId === currentSelectedLine.itemId &&
      saleLine.itemType === currentSelectedLine.itemType &&
      saleLine.level === currentSelectedLine.level &&
      saleLine.lineNumber === currentSelectedLine.lineNumber &&
      saleLine.partCode === currentSelectedLine.partCode) {
      newSelectedLine = saleLine
      break
    }
  }

  return newSelectedLine
}

export function getOpenOption(saleLines) {
  if (saleLines == null) {
    return null
  }

  for (let i = 0, j = 0; i < saleLines.length; i++) {
    if (i >= j && j < saleLines.length) {
      const line = saleLines[i]
      if (parseFloat(line.qty) === 0) {
        for (j = i + 1; j < saleLines.length; j++) {
          const optionSonLine = saleLines[j]
          if (parseFloat(line.level) >= parseFloat(optionSonLine.level)) {
            break
          }
        }
      } else if ((line.itemType === 'OPTION') && parseFloat(line.chosenQty || '0') < parseFloat(line.defaultQty)) {
        return line
      }
    }
  }

  return null
}
