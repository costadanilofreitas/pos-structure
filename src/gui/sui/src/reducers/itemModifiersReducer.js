class ModifiersParser {
  constructor() {
    this.itemIdsInState = []
    this.alreadyAddedToState = []
    this.newState = null
    this.removedModifierSets = []
    this.remainingModifierSets = []
  }

  parse(modifier) {
    this.newState = {
      productName: modifier['@attributes'].productName,
      itemId: modifier['@attributes'].itemId,
      modifiers: []
    }

    this.addDirectSonsOfModifierToState(modifier)
    this.removeNoDirectSons(modifier)
    this.addIndirectSonsOfModifierToState(this.remainingModifierSets)
    this.addRemovedItemsToCorrectParent()

    return this.newState
  }

  addRemovedItemsToCorrectParent() {
    while (this.removedModifierSets.length > 0) {
      this.newState.modifiers.some(modifier => {
        return this.searchRemovedModifierSetsInModifierTree(modifier)
      })
    }
  }

  searchRemovedModifierSetsInModifierTree(stateModifier) {
    return stateModifier.options.some(option => {
      const modifierSets = this.findModifierSetsForOption(stateModifier, option)
      if (modifierSets != null) {
        return this.addModifierSetsToOption(modifierSets, option)
      }
      return option.modifiers.some(innerModifier => {
        return this.searchRemovedModifierSetsInModifierTree(innerModifier)
      })
    })
  }

  addModifierSetsToOption(modifierSets, option) {
    this.addModifierSetsToState(modifierSets, option.modifiers)
    const index = this.removedModifierSets.indexOf(modifierSets)
    this.removedModifierSets.splice(index, 1)
    return true
  }

  findModifierSetsForOption(stateModifier, option) {
    const itemId = `${stateModifier.itemId}.${option.partCode}`

    let foundModifierSets = null
    this.removedModifierSets.some(modifierSets => {
      if (modifierSets['@attributes'].itemId === itemId) {
        foundModifierSets = modifierSets
        return true
      }
      return false
    })
    return foundModifierSets
  }

  addDirectSonsOfModifierToState(modifier) {
    modifier.ModifierSets.forEach(modifierSets => {
      if (this.isDirectSonOfModifiers(modifierSets)) {
        this.alreadyAddedToState.push(modifierSets['@attributes'].itemId)
        this.addModifierSetsToState(modifierSets, this.newState.modifiers)
      }
    })
  }

  removeNoDirectSons(modifier) {
    modifier.ModifierSets.forEach(modifierSets => {
      if (this.isAlreadyAddedToState(modifierSets)) {
        return
      }

      if (this.isDescendentOfAModifierAlreadyAdded(modifierSets)) {
        this.removedModifierSets.push(modifierSets)
      } else {
        this.remainingModifierSets.push(modifierSets)
      }
    })
  }

  isDescendentOfAModifierAlreadyAdded(modifierSets) {
    return this.itemIdsInState.some(toTrim => {
      return modifierSets['@attributes'].itemId.startsWith(toTrim)
    })
  }

  isAlreadyAddedToState(modifierSets) {
    return this.alreadyAddedToState.indexOf(modifierSets['@attributes'].itemId) >= 0
  }

  addIndirectSonsOfModifierToState(remainingModifierSets) {
    remainingModifierSets.forEach(modifierSets => {
      this.addModifierSetsToState(modifierSets, this.newState.modifiers)
    })
  }

  addModifierSetsToState(modifierSets, modifiers) {
    modifierSets.ModifierSet.forEach(modifierSet => {
      this.addModifierSetToState(modifierSets, modifierSet, modifiers)
    })
  }

  isDirectSonOfModifiers(modifierSets) {
    return this.newState.itemId === modifierSets['@attributes'].itemId
  }

  addModifierSetToState(modifierSets, modifierSet, modifiers) {
    this.itemIdsInState.push(`${modifierSets['@attributes'].itemId}.${modifierSet['@attributes'].partCode}`)

    const stateModifierSet = {
      itemId: `${modifierSets['@attributes'].itemId}.${modifierSet['@attributes'].partCode}`,
      productName: modifierSet['@attributes'].productName,
      displayName: modifierSet['@attributes'].displayName,
      options: []
    }

    modifierSet.Modifier.forEach(modifier => {
      stateModifierSet.options.push({
        partCode: modifier['@attributes'].partCode,
        productName: modifier['@attributes'].productName,
        modifiers: []
      })
    })

    modifiers.push(stateModifierSet)
  }
}

export default function itemModifiersReducer(state, action) {
  if (action.type === 'SET_PRODUCT_MODIFIERS') {
    if (action.payload == null ||
        action.payload.Modifiers == null ||
        action.payload.Modifiers.ModifierSets == null ||
        action.payload.Modifiers.ModifierSets.length == null ||
        action.payload.Modifiers.ModifierSets.length === 0) {
      return null
    }

    return new ModifiersParser().parse(action.payload.Modifiers)
  }

  if (state != null) {
    return state
  }

  return null
}
