import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import ItemModifierRenderer from './item-modifier-renderer'
import SelectedProductModifiersRetriever from './SelectedProductModifiersRetriever'
import SelectedModifierOptionsRetriever from './SelectedModifierOptionsRetriever'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'


export default class ItemModifier extends Component {
  constructor(props) {
    super(props)

    this.state = {}
    this.handleOnModifierSelected = this.handleOnModifierSelected.bind(this)
    this.handleOnOptionSelect = this.handleOnOptionSelect.bind(this)
    this.handleOnModifierTypeClick = this.handleOnModifierTypeClick.bind(this)
  }

  static createProductsWithRootProduct(rootProductPartCode, modifiers) {
    return [{
      itemId: rootProductPartCode,
      name: modifiers.modifiers[rootProductPartCode] == null ? '' : modifiers.modifiers[rootProductPartCode].name
    }]
  }

  static addNewProduct(rootProduct, modifier, option, products) {
    products.push({
      itemId: `${modifier.itemId}.${option.partCode}`,
      name: option.productName
    })
  }

  static isOptionSold(product, modifier, option, saleLines) {
    const lineId = `1.${modifier.itemId}.${option.partCode}`
    const optionSaleLine = saleLines
      .find(saleLine => `${saleLine['@attributes'].itemId}.${saleLine['@attributes'].partCode}` === lineId)
    return optionSaleLine != null && parseFloat(optionSaleLine['@attributes'].qty) > 0
  }

  static getProductModifiers(product, modifiers, itemType) {
    return new SelectedProductModifiersRetriever(modifiers, product, itemType).get()
  }

  static getSelectedModifierOptions(props, state) {
    return new SelectedModifierOptionsRetriever(
      state.selectedModifier,
      props.saleLines,
      state.specialModifier,
      props.modifiers,
      props.staticConfig.specialModifiers)
      .getOptions()
  }

  static getModifierOptions(modifiers, specialModifiers, modifier, saleLines) {
    return new SelectedModifierOptionsRetriever(
      modifier.itemId,
      saleLines,
      true,
      modifiers,
      specialModifiers)
      .getOptions()
  }

  static forEveryOptionOfSelectedProductModifiers(partCode, saleLines, modifiers, specialModifiers, func) {
    const itemType = saleLines[0]['@attributes'].itemType
    ItemModifier.getProductModifiers(partCode, modifiers, itemType)
      .forEach(modifier => {
        ItemModifier.getModifierOptions(modifiers, specialModifiers, modifier, saleLines)
          .options
          .forEach(option => {
            func(modifier, option)
          })
      })
  }

  static getProducts(modifiers, specialModifiers, saleLines) {
    const rootProductPartCode = saleLines[0]['@attributes'].partCode
    const products = ItemModifier.createProductsWithRootProduct(rootProductPartCode, modifiers)
    const hasModifiers = (option, modifiersList) => modifiersList.modifiers[option.partCode] != null
    ItemModifier.forEveryOptionOfSelectedProductModifiers(rootProductPartCode, saleLines, modifiers, specialModifiers,
      (modifier, option) => {
        if (hasModifiers(option, modifiers) &&
          ItemModifier.isOptionSold(rootProductPartCode, modifier, option, saleLines)) {
          ItemModifier.addNewProduct(rootProductPartCode, modifier, option, products)
        }
      })

    return products
  }

  static getSaleLine(lineId, saleLines) {
    const line = saleLines.find((saleLine) => (
      `${saleLine['@attributes'].itemId}.${saleLine['@attributes'].partCode}` === lineId
    ))

    if (line !== undefined) {
      Object.keys(line['@attributes'])
        .forEach(k => (line[k] = line['@attributes'][k]))
    }
    return line
  }

  static getSelectedProductModifiers(modifiers, saleLines, product) {
    const selectedProduct = `1.${product}`
    const itemType = ItemModifier.getSaleLine(selectedProduct, saleLines).itemType
    return ItemModifier.getProductModifiers(product, modifiers, itemType)
  }

  render() {
    const { modifiers, saleLines } = this.props
    const { specialModifiers } = this.props.staticConfig
    if (modifiers == null || modifiers.modifiers == null || modifiers.descriptions == null) {
      return null
    }

    if (this.state.selectedModifier == null) {
      return null
    }

    let selectedProductModifiers = []
    const products = ItemModifier.getProducts(modifiers, specialModifiers, saleLines)
    _.forEach(products, (product) => {
      selectedProductModifiers.push(...ItemModifier.getSelectedProductModifiers(modifiers, saleLines, product.itemId))
    })
    const selectedModifierOptions = ItemModifier.getSelectedModifierOptions(this.props, this.state)
    selectedProductModifiers = selectedProductModifiers.filter(x => !x.isCombo)

    return (
      <ItemModifierRenderer
        selectedProductModifiers={selectedProductModifiers}
        selectedModifier={this.state.selectedModifier}
        selectedModifierOptions={selectedModifierOptions}
        specialModifier={this.state.specialModifier}
        onModifierSelect={this.handleOnModifierSelected}
        onOptionSelect={this.handleOnOptionSelect}
        onModifierTypeClick={this.handleOnModifierTypeClick}
        selectedQty={this.props.selectedQty}
        onQtyChange={this.props.onQtyChange}
        mobile={this.props.mobile}
        deviceType={this.props.deviceType}
        products={this.props.products}
      />
    )
  }

  handleOnModifierSelected(itemId, props, changeState) {
    let selectedParent = this.props.saleLines[0]
    const selectedLine = this.getSelectedChild(`1.${itemId}`, props)
    if (props != null) {
      selectedParent = props.saleLines[0]
    }

    if (changeState !== false) {
      this.setState(
        {
          selectedModifier: itemId,
          specialModifier: 'INC'
        })
    }

    this.props.onLineClick(selectedLine, selectedParent, true, true)
  }

  handleOnOptionSelect(type, partCode) {
    const selectedOption = this.getSelectedOption(partCode)

    if (type === 'mod') {
      this.handleModifierSale(selectedOption)
    } else {
      this.handleOptionSale(selectedOption)
    }
  }

  getNewOptionQuantity(partId, otherOptionsQty, specialModifier, selectedQty, maxOptionQty, specialModifiers) {
    const currentOptionQty = this.getOptionQty(partId)
    if (specialModifiers.includes(specialModifier) && currentOptionQty > 0) {
      return currentOptionQty
    }

    if (specialModifier === 'DEC') {
      return selectedQty >= currentOptionQty ? 0 : currentOptionQty - selectedQty
    }

    const maxItemQty = maxOptionQty - otherOptionsQty
    return selectedQty + currentOptionQty > maxItemQty ? maxItemQty - currentOptionQty : selectedQty
  }

  getOptionMaxQty(optionSaleLine) {
    if (optionSaleLine.maxQty != null) {
      return parseFloat(optionSaleLine.maxQty)
    }
    const [optionContext, optionCode] = _.takeRight(this.state.selectedModifier.split('.'), 2)
    const { modifiers } = this.props.modifiers
    return parseFloat(modifiers[optionContext].parts[optionCode].data.maxQty)
  }

  handleOptionSale(selectedOption) {
    const { specialModifier } = this.state
    const partCode = selectedOption.partCode
    const itemId = `1.${this.state.selectedModifier}`
    let autoExitModScreen = false
    let currentSelectedPart

    const partId = `1.${this.state.selectedModifier}.${partCode}`
    let otherOptionsQty = 0
    const optionSaleLine = ItemModifier.getSaleLine(itemId, this.props.saleLines)
    const maxOptionQty = this.getOptionMaxQty(optionSaleLine)

    const sons = this.getAllSonsOfLine(optionSaleLine)
    if (maxOptionQty === 1) {
      currentSelectedPart = sons.find(son => parseFloat(son['@attributes'].qty) > 0)
    } else {
      const optionQty = sons.reduce((sonQty, son) => sonQty + parseFloat(son['@attributes'].qty), 0)
      if (specialModifier !== 'DEC') {
        const lineId = `${this.props.selectedLine.itemId}.${this.props.selectedLine.partCode}`
        currentSelectedPart = sons.find(son => (`${son.itemId}.${son.partCode}`) === lineId)
      }

      const currentSelectedLineQty = currentSelectedPart ? parseFloat(currentSelectedPart.qty) : 0
      otherOptionsQty = optionQty - this.getOptionQty(partId) - currentSelectedLineQty
    }

    const selectedQty = this.props.selectedQty
    const specialModifiers = this.props.staticConfig.specialModifiers
    const qty = this.getNewOptionQuantity(
      partId, otherOptionsQty, specialModifier, selectedQty, maxOptionQty, specialModifiers)
    if (maxOptionQty <= otherOptionsQty + qty) {
      autoExitModScreen = this.props.autoExitModifierScreen === true
    }
    let subst

    if (specialModifier === 'DEC') {
      subst = `.${partCode.toString()}`
    } else if (currentSelectedPart != null) {
      const selectedPartCode = currentSelectedPart['@attributes'].partCode.toString()
      subst = `.${selectedPartCode}`
    }

    const comment = ['INC', 'DEC'].includes(specialModifier) === true ? '' : specialModifier
    this.props.onSellOption({ product_code: partCode }, itemId, subst, autoExitModScreen, qty, comment)
  }

  getOptionQty(partId) {
    const saleLine = ItemModifier.getSaleLine(partId, this.props.saleLines)
    if (saleLine != null) {
      return parseFloat(saleLine['@attributes'].qty)
    } else if (this.props.modifiers.defaultQuantities != null) {
      let fullItemId = partId.split('.')
        .slice(1)
        .join('.')
      while (fullItemId.split('.').length > 1) {
        const modifierParts = this.props.modifiers.defaultQuantities[fullItemId]
        if (modifierParts !== undefined && modifierParts !== null) {
          return parseFloat(modifierParts)
        }

        fullItemId = fullItemId.split('.')
          .slice(1)
          .join('.')
      }
    }
    return 0
  }

  getAllSonsOfLine(optionLine) {
    const sons = []
    this.props.saleLines.forEach(line => {
      if (line['@attributes'].itemId === `${optionLine['@attributes'].itemId}.${optionLine['@attributes'].partCode}`) {
        sons.push(line)
      }
    })
    return sons
  }

  getSelectedOption(partCode) {
    const optionRetriever = new SelectedModifierOptionsRetriever(
      this.state.selectedModifier,
      this.props.saleLines,
      this.state.specialModifier,
      this.props.modifiers)

    return optionRetriever.getOptions()
      .options
      .find((option) => (option.partCode === partCode))
  }

  handleModifierSale(selectedOption) {
    const partCode = selectedOption.partCode
    const modifierLine = ItemModifier.getSaleLine(`1.${this.state.selectedModifier}`, this.props.saleLines)

    let qty
    let modType = this.state.specialModifier
    if (modType === 'INC' || modType === 'DEC') {
      const modifierId = `1.${this.state.selectedModifier}.${partCode}`
      qty = this.getModifierQty(selectedOption, modifierId)
      modType = undefined
    } else {
      qty = this.props.modifiers.modifiers[modifierLine.partCode].parts[partCode].data.defaultQty
      qty = parseFloat(qty) === 0 ? 1 : qty
    }

    this.props.onSellModifier({ product_code: partCode }, modifierLine, modType, qty)
  }

  getModifierQty(selectedOption, modifierId) {
    const modifierLine = ItemModifier.getSaleLine(modifierId, this.props.saleLines)
    const selectedQty = this.props.selectedQty

    let qty = typeof selectedOption.selected === 'number' ? parseFloat(selectedOption.selected) : 1
    if (modifierLine != null) {
      qty = parseFloat(modifierLine['@attributes'].qty)
    }

    if (this.state.specialModifier !== 'DEC') {
      qty = selectedOption.maxQty < qty + selectedQty ? selectedOption.maxQty : qty + selectedQty
    } else {
      qty = selectedOption.minQty > qty - selectedQty ? selectedOption.minQty : qty - selectedQty
    }
    return qty
  }

  getSelectedChild(modifierId, props) {
    let saleLines = this.props.saleLines
    if (props != null) {
      saleLines = props.saleLines
    }

    return ItemModifier.getSaleLine(modifierId, saleLines)
  }

  handleOnModifierTypeClick(value) {
    this.setState({ specialModifier: value })
  }

  static getDerivedStateFromProps(props, state = null) {
    let nextState = { ...(state ?? {}) }
    const { modifiers, saleLines } = props
    const { specialModifiers } = props.staticConfig
    let selectedProductModifiers = []
    const products = ItemModifier.getProducts(modifiers, specialModifiers, saleLines)
    _.forEach(products, (product) => {
      selectedProductModifiers.push(...ItemModifier.getSelectedProductModifiers(modifiers, saleLines, product.itemId))
    })

    selectedProductModifiers = selectedProductModifiers.filter(x => !x.isCombo)
    if (selectedProductModifiers.length === 0) {
      nextState = {
        ...nextState,
        selectedModifier: null,
        specialModifier: null,
        lineNumber: props.selectedLine.lineNumber
      }
      return nextState
    }

    let selectedModifier = null
    let lineId = `${props.selectedLine.itemId}.${props.selectedLine.partCode}`
    const a = modifier => (`1.${modifier.itemId}`) === lineId
    while (lineId) {
      selectedModifier = selectedProductModifiers.find(a)
      if (selectedModifier != null) {
        break
      }
      lineId = lineId.substring(0, lineId.lastIndexOf('.'))
    }

    if (selectedModifier == null) {
      const itemId = selectedProductModifiers[0].itemId
      const selectedParent = props.saleLines[0]
      const selectedLine = ItemModifier.getSaleLine(`1.${itemId}`, saleLines)
      props.onLineClick(selectedLine, selectedParent, true, true)
    }

    selectedModifier = selectedModifier == null ? selectedProductModifiers[0].itemId : selectedModifier.itemId
    let specialModifier = 'INC'
    if (state != null) {
      specialModifier = state.specialModifier
      const lineNumber = props.saleLines[0]['@attributes'].lineNumber
      if (selectedModifier !== state.selectedModifier || lineNumber !== state.lineNumber) {
        specialModifier = 'INC'
      }
    }

    const tempState = { ...nextState, selectedModifier, specialModifier }
    const selectedModifierOptions = ItemModifier.getSelectedModifierOptions(props, tempState)
    const canAddQty = _.find(selectedModifierOptions.options, (item) => {
      return item.selected < item.maxQty
    })

    if (canAddQty == null) {
      specialModifier = 'DEC'
    }

    return {
      ...nextState,
      selectedModifier: selectedModifier,
      specialModifier: specialModifier,
      lineNumber: props.selectedLine.lineNumber
    }
  }
}

const modifierShape = PropTypes.shape({
  modifiers: PropTypes.object,
  descriptions: PropTypes.object
})

ItemModifier.propTypes = {
  modifiers: modifierShape,
  saleLines: PropTypes.arrayOf(PropTypes.shape({
    '@attributes': PropTypes.shape({
      lineNumber: PropTypes.string,
      partCode: PropTypes.string,
      itemType: PropTypes.string
    })
  })),
  selectedLine: PropTypes.object,
  onSellOption: PropTypes.func,
  onSellModifier: PropTypes.func,
  staticConfig: StaticConfigPropTypes,
  autoExitModifierScreen: PropTypes.bool,
  selectedQty: PropTypes.number,
  onQtyChange: PropTypes.func,
  onLineClick: PropTypes.func,
  mobile: PropTypes.bool,
  deviceType: PropTypes.number,
  products: PropTypes.object
}
