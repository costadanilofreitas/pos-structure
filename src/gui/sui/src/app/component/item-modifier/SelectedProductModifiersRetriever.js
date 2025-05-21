export default class SelectedProductModifiersRetriever {
  constructor(modifiers, selectedProduct, itemType) {
    this.modifiers = modifiers
    this.selectedProduct = selectedProduct

    this.itemType = itemType
    this.noOptionParts = []
    this.selectedProductModifiers = []
  }

  get() {
    this.addDirectOptionsToModifiers()
    this.addIndirectOptionsToModifiers()
    return this.selectedProductModifiers
  }

  addDirectOptionsToModifiers() {
    this.getSelectedProductParts().forEach(partCode => {
      const selectedProductPart = this.getSelectedProductPart(partCode)
      if (selectedProductPart.isOption) {
        this.selectedProductModifiers.push({
          itemId: `${this.selectedProduct}.${partCode}`,
          productName: this.modifiers.descriptions[partCode],
          type: this.getSelectedProductPart(partCode).data.maxQty === '1' ? 'single' : 'multi',
          maxQty: parseFloat(this.getSelectedProductPart(partCode).data.maxQty),
          isCombo: selectedProductPart != null ? selectedProductPart.isCombo : false
        })
      } else {
        this.noOptionParts.push(partCode)
      }
    })

    if (this.itemType !== 'COMBO') {
      if (this.noOptionParts.length !== 0) {
        const parts = this.selectedProduct.split('.')
        const partCode = parts[parts.length - 1]
        const selectedProductPart = this.getSelectedProductPart(partCode)
        this.selectedProductModifiers.push({
          itemId: this.selectedProduct,
          productName: [this.modifiers.descriptions[partCode], '* MODIFICADORES *'],
          type: 'mod',
          maxQty: 99,
          isCombo: selectedProductPart != null ? selectedProductPart.isCombo : false
        })
      }
      this.noOptionParts = []
    }
  }

  addIndirectOptionsToModifiers() {
    let directModifiers = null
    this.noOptionParts.forEach(partCode => {
      this.getProductParts(partCode).forEach(innerPartCode => {
        if (this.modifiers.modifiers[partCode] == null) {
          return
        }

        const selectedProductPart = this.getSelectedProductPart(partCode)
        if (this.modifiers.modifiers[partCode].parts[innerPartCode].isOption) {
          this.selectedProductModifiers.push({
            itemId: `${this.selectedProduct}.${partCode}.${innerPartCode}`,
            productName: [this.modifiers.descriptions[partCode], this.modifiers.descriptions[innerPartCode]],
            type: this.modifiers.modifiers[partCode].parts[innerPartCode].data.maxQty === '1' ? 'single' : 'multi',
            maxQty: parseFloat(this.modifiers.modifiers[partCode].parts[innerPartCode].data.maxQty),
            isCombo: selectedProductPart.isCombo
          })
        } else {
          directModifiers = directModifiers != null ? directModifiers : {
            itemId: `${this.selectedProduct}.${partCode}`,
            productName: [this.modifiers.descriptions[partCode], '* MODIFICADORES *'],
            type: 'mod',
            maxQty: 99,
            isCombo: selectedProductPart.isCombo
          }
        }
      })
      if (directModifiers != null) {
        this.selectedProductModifiers.push(directModifiers)
        directModifiers = null
      }
    })
  }

  getProductParts(itemId) {
    const parts = itemId.split('.')
    const partCode = parts[parts.length - 1]

    if (this.modifiers.modifiers[partCode] != null) {
      return Object.keys(this.modifiers.modifiers[partCode].parts)
    }

    return []
  }

  getSelectedProductParts() {
    return this.getProductParts(this.selectedProduct)
  }

  getSelectedProductPart(partCode) {
    const parts = this.selectedProduct.split('.')
    const productPartCode = parts[parts.length - 1]
    return this.modifiers.modifiers[productPartCode].parts[partCode]
  }
}
