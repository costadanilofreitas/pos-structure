export default class SelectedModifierOptionsRetriever {
  constructor(selectedModifier, saleLines, specialModifier, modifiers, specialModifiers) {
    this.selectedModifier = selectedModifier
    this.saleLines = saleLines
    this.specialModifier = specialModifier
    this.modifiers = modifiers
    this.specialModifiers = specialModifiers || []
  }

  getOptions() {
    const selectedModifierPart = this.getSelectedModifierPart()

    let modifierPartList = []
    let singleSelectionModifier
    if (this.isPartModifier(selectedModifierPart)) {
      const partsModifier = this.selectedModifier.split('.')
      const innerParts = this.modifiers.modifiers[partsModifier[partsModifier.length - 1]].parts
      Object.keys(innerParts).forEach(key => {
        if (!innerParts[key].isOption) {
          modifierPartList.push(key)
        }
      })
      singleSelectionModifier = false
    } else {
      modifierPartList = selectedModifierPart.data.options
      singleSelectionModifier = this.isSingleSelectionModifier(selectedModifierPart)
    }

    const selectedModifierOptions = []
    modifierPartList.forEach(option => {
      if (this.specialModifier !== 'DEC' || this.getSelectedQuantity(option) > 0) {
        selectedModifierOptions.push({
          context: this.selectedModifier,
          partCode: parseInt(option, 10),
          productName: this.modifiers.descriptions[option],
          selected: this.getSelected(selectedModifierPart, option),
          minQty: this.getMinQty(selectedModifierPart, option),
          maxQty: this.getMaxQty(selectedModifierPart, option)
        })
      }
    })

    return {
      options: selectedModifierOptions,
      singleSelectionModifier,
      specialModifiers: this.specialModifiers,
      maxQty: selectedModifierPart == null ? 99 : selectedModifierPart.data.maxQty
    }
  }

  changeSelectedLine(partCode) {
    const modifierId = this.getModifierId()
    const currentlySelectedSaleLine = this.getCurrentlySelectedSaleLine(modifierId)
    if (currentlySelectedSaleLine != null) {
      if (currentlySelectedSaleLine['@attributes'].oldQty != null) {
        this.removeSaleLineWithSons(currentlySelectedSaleLine)

        const willBeSelectedLineId = `1.${this.selectedModifier}.${partCode}`
        const currentlySelectedLineId = `${currentlySelectedSaleLine['@attributes'].itemId}.${currentlySelectedSaleLine['@attributes'].partCode}`

        if (this.getSelectedModifierPart().data.minQty === '0') {
          if (willBeSelectedLineId === currentlySelectedLineId) {
            return
          }
        }
      } else {
        currentlySelectedSaleLine['@attributes'].oldQty = currentlySelectedSaleLine['@attributes'].qty
        currentlySelectedSaleLine['@attributes'].newQty = '0'
        currentlySelectedSaleLine['@attributes'].qty = '0'
      }
    }

    const saleLine = this.getWillBeSelectedSaleLine(partCode)

    if (saleLine != null) {
      delete saleLine['@attributes'].oldQty
      delete saleLine['@attributes'].newQty
      saleLine['@attributes'].qty = '1'
    } else {
      this.addNewSaleLine(partCode, 0, 1)
    }
  }

  removeSaleLineWithSons(lineToRemove) {
    const linesToRemove = [lineToRemove]
    this.saleLines.forEach(saleLine => {
      if (saleLine['@attributes'].itemId.startsWith(
        `${lineToRemove['@attributes'].itemId}.${lineToRemove['@attributes'].partCode}`)) {
        linesToRemove.push(saleLine)
      }
    })

    linesToRemove.forEach(saleLine => {
      const index = this.saleLines.indexOf(saleLine)
      this.saleLines.splice(index, 1)
    })
  }

  changeQuantityOfSelectedLine(partCode) {
    const increment = this.incrementing ? 1 : -1

    const selectedSaleLine = this.getOptionSaleLine(partCode)
    if (selectedSaleLine == null) {
      this.addNewLineIfQuantityIsPositiveOrZero(increment, partCode)
    } else {
      this.changeLineQuantityIfIsPositiveOrZero(selectedSaleLine, increment)
    }
  }

  changeLineQuantityIfIsPositiveOrZero(saleLine, increment) {
    const optionLine = this.getOptionOfSaleLine(saleLine)
    const sons = this.getAllSonsOfLine(optionLine)
    let optionSelectedQuantity = 0
    sons.forEach(son => {
      optionSelectedQuantity += parseFloat(son['@attributes'].qty)
    })
    optionSelectedQuantity += increment
    const modifierPart = this.getSelectedModifierPart()
    if (optionSelectedQuantity >= parseFloat(modifierPart.data.minQty) &&
        optionSelectedQuantity <= parseFloat(modifierPart.data.maxQty)) {
      const saleLineQty = parseFloat(saleLine['@attributes'].qty) + increment
      if (saleLineQty >= 0) {
        saleLine['@attributes'].qty = saleLineQty.toString()
        if (saleLine['@attributes'].qty === saleLine['@attributes'].defaultQty) {
          this.removeSaleLineWithSons(saleLine)
          this.removeEmptyCreatedOptions(saleLine)
        }
      }
    }
  }

  removeEmptyCreatedOptions(saleLine) {
    const optionLine = this.getCreatedOptionOfSaleLine(saleLine)
    if (optionLine != null) {
      if (this.getFirstSonOfLine(optionLine) == null) {
        this.removeSaleLineWithSons(optionLine)
      }
    }
  }

  getFirstSonOfLine(optionLine) {
    return this.saleLines.find(line =>
      line['@attributes'].itemId === `${optionLine['@attributes'].itemId}.${optionLine['@attributes'].partCode}`)
  }

  getAllSonsOfLine(optionLine) {
    const sons = []
    this.saleLines.forEach(line => {
      if (line['@attributes'].itemId === `${optionLine['@attributes'].itemId}.${optionLine['@attributes'].partCode}`) {
        sons.push(line)
      }
    })
    return sons
  }

  getCreatedOptionOfSaleLine(saleLine) {
    const optionLine = this.getSaleLineById(saleLine['@attributes'].itemId)
    if (optionLine != null && optionLine['@attributes'].oldQty != null) {
      return optionLine
    }
    return undefined
  }

  getOptionOfSaleLine(saleLine) {
    return this.getSaleLineById(saleLine['@attributes'].itemId)
  }

  getWillBeSelectedSaleLine(partCode) {
    const optionId = `1.${this.selectedModifier}.${partCode}`
    return this.getSaleLineById(optionId)
  }

  getCurrentlySelectedSaleLine(modifierId) {
    return this.saleLines.find(saleLine => saleLine['@attributes'].itemId === modifierId && this.hasQuantity(saleLine))
  }

  getSaleLineById(lineId) {
    return this.saleLines.find(saleLine =>
      `${saleLine['@attributes'].itemId}.${saleLine['@attributes'].partCode}` === lineId)
  }

  hasQuantity(saleLine) {
    return parseFloat(saleLine['@attributes'].qty) > 0
  }

  getModifierId() {
    return `1.${this.selectedModifier}`
  }

  getSelectedModifierPart() {
    const splitCode = this.selectedModifier.split('.')

    if (splitCode.length === 1) {
      return this.modifiers.modifiers[this.selectedModifier].parts[0]
    }
    if (this.modifiers.modifiers[splitCode[splitCode.length - 2]] != null) {
      return this.modifiers.modifiers[splitCode[splitCode.length - 2]].parts[splitCode[splitCode.length - 1]]
    }
    return null
  }

  getSelected(selectedModifier, option) {
    let selected
    if (this.isSingleSelectionModifier(selectedModifier)) {
      selected = this.isOptionSelected(option)
    } else {
      selected = this.getSelectedQuantity(option)
    }
    return selected
  }

  isOptionSelected(option) {
    const optionSaleLine = this.getOptionSaleLine(option)
    return optionSaleLine != null && parseFloat(optionSaleLine['@attributes'].qty) > 0
  }

  getSelectedQuantity(option) {
    const currentSaleLine = this.getOptionSaleLine(option)
    if (currentSaleLine != null) {
      return parseFloat(currentSaleLine['@attributes'].qty)
    }

    return this.getDefaultQuantity(option)
  }

  getDefaultQuantity(optionPartCode) {
    const parts = this.selectedModifier.split('.')
    const partCode = parts[parts.length - 1]

    const modifier = this.modifiers.modifiers[partCode]
    if (modifier != null) {
      const modifierParts = this.modifiers.modifiers[partCode].parts[optionPartCode]
      if (modifierParts != null) {
        return parseFloat(this.modifiers.modifiers[partCode].parts[optionPartCode].data.defaultQty)
      }
    } else if (this.modifiers.defaultQuantities != null) {
      let fullItemId = `${this.selectedModifier}.${optionPartCode}`
      while (fullItemId.split('.').length > 1) {
        const modifierParts = this.modifiers.defaultQuantities[fullItemId]
        if (modifierParts != null) {
          return parseFloat(modifierParts)
        }

        fullItemId = fullItemId.split('.').slice(1).join('.')
      }
    }
    return 0
  }

  getOptionSaleLine(option) {
    const optionId = this.getOptionId(option)
    return this.saleLines.find(saleLine => this.getSaleLineId(saleLine) === optionId)
  }

  getOptionId(option) {
    return `1.${this.selectedModifier}.${option}`
  }

  getSaleLineId(saleLine) {
    return `${saleLine['@attributes'].itemId}.${saleLine['@attributes'].partCode}`
  }

  isSingleSelectionModifier(selectedModifier) {
    return !this.isPartModifier(selectedModifier) && selectedModifier.data.maxQty === '1'
  }

  getMaxQty(selectedModifierPart, option) {
    if (this.isPartModifier(selectedModifierPart)) {
      const partsModifier = this.selectedModifier.split('.')
      return parseFloat(this.modifiers.modifiers[partsModifier[partsModifier.length - 1]].parts[option].data.maxQty)
    }
    return 99
  }

  getMinQty(selectedModifierPart, option) {
    if (this.isPartModifier(selectedModifierPart)) {
      const partsModifier = this.selectedModifier.split('.')
      return parseFloat(this.modifiers.modifiers[partsModifier[partsModifier.length - 1]].parts[option].data.minQty)
    }
    return 0
  }

  isPartModifier(modifierPart) {
    return modifierPart == null || modifierPart.data.options == null
  }
}
