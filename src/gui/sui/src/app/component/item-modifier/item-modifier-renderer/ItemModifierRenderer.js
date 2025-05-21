import React from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import ActionButton from '../../../../component/action-button'
import ProductButton from '../../buttons/product-button'
import DeviceType from '../../../../constants/Devices'
import RendererChooser from '../../../../component/renderer-chooser'
import ButtonGrid from '../../button-grid/ButtonGrid'

function getModifierName(modName) {
  if (Array.isArray(modName)) {
    return modName.map((modifier, index) => <span key={index}> {modifier} </span>)
  }
  return modName
}

export default function ItemModifierRenderer(props) {
  const {
    classes, selectedProductModifiers, selectedModifier, onModifierSelect, selectedModifierOptions,
    onOptionSelect, specialModifier, onModifierTypeClick, mobile, deviceType
  } = props
  const activeModifier = selectedProductModifiers.find(modifier => (selectedModifier === modifier.itemId))

  function renderTabs() {
    const buttons = {}
    selectedProductModifiers.forEach((modifier, index) => {
      const selected = selectedModifier === modifier.itemId
      const onClickAction = () => onModifierSelect(modifier.itemId)
      const className = `${classes.tabItem} ${selected ? classes.tabItemSelected : ''} test_ItemModifierRenderer_${index}`

      const defaultButton = (
        <ActionButton
          onClick={onClickAction}
          className={className}
        >
          {getModifierName(modifier.productName)}
        </ActionButton>
      )

      const totemButton = (
        <ActionButton
          onClick={onClickAction}
          className={className}
          style={{ borderRadius: '5px' }}
        >
          {getModifierName(modifier.productName)}
        </ActionButton>
      )

      buttons[index] = (
        <RendererChooser
          desktop={defaultButton}
          mobile={defaultButton}
          totem={totemButton}
        />
      )
    })
    return buttons
  }

  function renderItems() {
    const buttons = {}

    selectedModifierOptions.options.forEach((option, index) => {
      const functionHandler = () => onOptionSelect(activeModifier.type, option.partCode)
      const selected = option.selected === true || option.selected > 0

      function getMainContainerStyle() {
        let mainContainerStyle = { background: '#FFFFFF', fontSize: '1.5vmin' }

        if (deviceType !== DeviceType.Totem) {
          mainContainerStyle = { border: 'none', borderRadius: '0', boxShadow: 'none' }
        }
        if (deviceType === DeviceType.Mobile) {
          mainContainerStyle.fontSize = '3vmin'
        }

        return mainContainerStyle
      }

      buttons[index] = (
        <ProductButton
          code={`${option.context}.${option.partCode.toString()}`}
          addBgColor={deviceType !== DeviceType.Totem}
          bgColor={'lightgray'}
          buttonSpacing={deviceType === DeviceType.Totem ? '5%' : '0.4vmin'}
          quantityContainerStyle={deviceType === DeviceType.Totem ? {
            justifyContent: 'center',
            fontWeight: 'bold'
          } : {}}
          mainContainerStyle={getMainContainerStyle()}
          showQuantity={true}
          selected={selected}
          quantity={parseInt(option.selected, 10)}
          showImage={deviceType === DeviceType.Totem}
          showValue={deviceType === DeviceType.Totem}
          onClick={functionHandler}
          showSelectedBorderBottom={true}
        >
        </ProductButton>
      )
    })

    return buttons
  }

  function renderModifiers() {
    if (selectedModifierOptions.specialModifiers == null) {
      return null
    }

    return selectedModifierOptions.specialModifiers.map((specialMod, index) => {
      return (
        <FlexChild key={index} size={1}>
          <ActionButton
            className={`test_ItemModifierRenderer_${specialMod.replace('$', '')}`}
            selected={specialModifier === specialMod}
            onClick={() => onModifierTypeClick(specialMod)}
          >
            <I18N id={specialMod}/>
          </ActionButton>
        </FlexChild>)
    })
  }

  const mobileTabs = selectedProductModifiers.length < 5 ? 5 : selectedProductModifiers.length
  const desktopTabs = selectedProductModifiers.length < 8 ? 8 : selectedProductModifiers.length

  function getRowQuantities() {
    let quantityOfRows = 9
    if (deviceType === DeviceType.Mobile) {
      quantityOfRows = 8
    } else if (deviceType === DeviceType.Totem) {
      quantityOfRows = 3
    }

    return quantityOfRows
  }

  const rowsQuantity = getRowQuantities()
  return (
    <FlexGrid direction={'column'} className={classes.container}>
      <FlexChild size={1} innerClassName={classes.container}>
        <FlexGrid direction={'row'}>
          <FlexChild size={1}>
            <ActionButton
              className={'test_ItemModifierRenderer_PLUS'}
              selected={specialModifier === 'INC'}
              onClick={() => onModifierTypeClick('INC')}
            >
              <i className={'fas fa-plus fa-2x'} aria-hidden="true" style={{ margin: '0.5vh' }}/>
            </ActionButton>
          </FlexChild>
          <FlexChild size={1}>
            <ActionButton
              className={'test_ItemModifierRenderer_MINUS'}
              selected={specialModifier === 'DEC'}
              onClick={() => onModifierTypeClick('DEC')}
            >
              <i className={'fas fa-minus fa-2x'} aria-hidden="true" style={{ margin: '0.5vh' }}/>
            </ActionButton>
          </FlexChild>
          {renderModifiers()}
        </FlexGrid>
      </FlexChild>
      <FlexChild size={mobile ? 7 : 8} innerClassName={classes.container}>
        <FlexGrid direction={'row'}>
          <FlexChild size={5} style={{ overflow: 'auto' }}>
            <ButtonGrid
              direction="row" cols={3}
              rows={rowsQuantity}
              buttons={renderItems()}
              styleCell={{ height: 'auto' }}
              renderWithScrollPanel={deviceType !== DeviceType.Totem}
            />
          </FlexChild>
          <FlexChild size={2} innerClassName={classes.tabs}>
            <ButtonGrid direction="row" cols={1} rows={mobile ? mobileTabs : desktopTabs} buttons={renderTabs()}/>
          </FlexChild>
        </FlexGrid>
      </FlexChild>
    </FlexGrid>
  )
}

ItemModifierRenderer.propTypes = {
  classes: PropTypes.object,
  selectedProductModifiers: PropTypes.arrayOf(PropTypes.shape({
    itemId: PropTypes.string,
    productName: PropTypes.oneOfType([PropTypes.array, PropTypes.string])
  })),
  selectedModifier: PropTypes.string,
  selectedModifierOptions: PropTypes.shape({
    options: PropTypes.arrayOf(PropTypes.shape({
      context: PropTypes.string,
      partCode: PropTypes.number,
      productName: PropTypes.string,
      selected: PropTypes.oneOfType([PropTypes.bool, PropTypes.number])
    })),
    singleSelectionModifier: PropTypes.bool,
    specialModifiers: PropTypes.arrayOf(PropTypes.string)
  }),
  specialModifier: PropTypes.string,
  onModifierSelect: PropTypes.func,
  onOptionSelect: PropTypes.func,
  onModifierTypeClick: PropTypes.func,
  mobile: PropTypes.bool,
  deviceType: PropTypes.number
}
