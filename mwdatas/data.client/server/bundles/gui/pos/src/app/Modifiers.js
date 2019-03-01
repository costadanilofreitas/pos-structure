import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { Button } from 'posui/button'
import { NavigationGrid } from 'posui/widgets'
import injectSheet, { jss } from 'react-jss'
import { I18N } from 'posui/core'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  container: {
    position: 'relative',
    width: '100%',
    height: '100%'
  },
  modTypesBox: {
    position: 'relative',
    height: '8%',
    width: '100%'
  },
  modTypeButton: {
    width: '9vh',
    height: '5vh',
    float: 'left',
    marginLeft: '1vh',
    border: '1px solid #cccccc'
  },
  modTypeButtonSelected: {
    backgroundColor: '#ed7801',
    color: '#762823'
  },
  modGroupsBox: {
    position: 'relative',
    height: '92%',
    width: '100%'
  },
  modsCont: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    boxSizing: 'border-box'
  },
  ingredient: {
    backgroundColor: '#ec7801',
    color: 'white'
  },
  ingredientRemoved: {
    backgroundColor: '#fff',
    border: '1px dashed #ec1c24 !important'
  },
  mod: {
    backgroundColor: '#ec7801',
    color: 'white'
  },
  modRemoved: {
    backgroundColor: '#fdbd10'
  },
  modQty: {
    position: 'absolute',
    right: '2px',
    top: '2px'
  },
  noMods: {
    color: '#777777'
  },
  title: {
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: '4.5vh',
    position: 'relative'
  }
}

const MAX_COLS = 7
const MAX_ROWS = 7
const MOD_TYPES = [
  {
    id: 'EXTRA',
    text: 'Extra'
  },
  {
    id: 'LIGHT',
    text: 'Light'
  },
  {
    id: 'ON_SIDE',
    text: 'On Side'
  }
]

class Modifiers extends PureComponent {

  state = {
    selectedModType: null
  }

  renderInfo = () => {
    const { order, modifiers, saleLine } = this.props
    const currentModifier = modifiers.modifiers[saleLine.partCode] || {}
    const parts = _.keys(currentModifier.parts || {})
    const ingredients = {
      text: 'Ingredients',
      name: 'Ingredients',
      classes: [],
      items: []
    }
    const mods = {
      text: 'Modifiers',
      name: 'Modifiers',
      classes: [],
      items: []
    }
    // get modifiers under current selected line only
    const level = parseInt(saleLine.level, 10)
    const filteredMods = []
    let found = false
    _.forEach(
      _.map(
        order.SaleLine || [],
        (saleLineItem) => saleLineItem['@attributes'] || {}
      ),
      (saleLineItem) => {
        if (_.isEqual(saleLine, saleLineItem)) {
          found = true
        } else if (found) {
          const itemLevel = parseInt(saleLineItem.level, 10)
          if (itemLevel > level) {
            if (_.includes(['INGREDIENT', 'CANADD'], saleLineItem.itemType)) {
              filteredMods.push(saleLineItem)
            }
          } else {
            found = false
          }
        }
      }
    )
    // modifier quantities for currently selected line
    const currentMods = _.fromPairs(
      _.map(
        filteredMods,
        (mod) => [mod.partCode, parseInt(mod.qty, 10)]
      )
    )
    const modGroups = []
    const modColsNeededByGroup = []
    _.forEach(parts, (partCode) => {
      const part = currentModifier.parts[partCode]
      const text = modifiers.descriptions[partCode]
      if (!part.isOption) {
        // ingredients and mods
        const data = part.data || {}
        const defaultQty = parseInt(data.defaultQty || '0', 10)
        const selected = _.has(currentMods, partCode) ?
          (currentMods[partCode] > 0) : Boolean(defaultQty)
        const isIngredient = defaultQty > 0
        const buttonData = {
          isIngredient,
          defaultQty,
          qty: _.has(currentMods, partCode) ? currentMods[partCode] : defaultQty,
          selected,
          text,
          plu: partCode,
          classes: [],
          bgColor: (selected) ? '#c0c0c0' : '#757a63'
        }
        if (isIngredient) {
          ingredients.items.push(buttonData)
        } else {
          mods.items.push(buttonData)
        }
      }
    })
    if (ingredients.items.length > 0) {
      modGroups.push(ingredients)
      modColsNeededByGroup.push(Math.ceil(ingredients.items.length / MAX_ROWS))
    }
    if (mods.items.length > 0) {
      modGroups.push(mods)
      modColsNeededByGroup.push(Math.ceil(mods.items.length / MAX_ROWS))
    }
    return {
      colsNeededByGroup: modColsNeededByGroup,
      groups: modGroups
    }
  }

  handleModTypeClick = (idx) => {
    const { selectedModType } = this.state
    const modType = (idx === selectedModType) ? null : idx
    this.setState({ selectedModType: modType })
  }

  handleSellModifier = (plu) => {
    const { saleLine } = this.props
    const { selectedModType } = this.state
    const modType = (selectedModType !== null) ? MOD_TYPES[selectedModType].id : 'TOGGLE'
    this.setState({ selectedModType: null })
    return this.props.sellModifier(plu, saleLine, modType)
  }

  handleRenderButton = (item, key, sellFunc) => {
    const { classes } = this.props
    const selected = Boolean(item.selected)
    const isDefault = item.qty === item.defaultQty
    let buttonClass = ''
    if (item.isIngredient) {
      buttonClass = (item.qty < 1 && !isDefault) ? classes.ingredientRemoved : classes.ingredient
    } else {
      buttonClass = (item.qty < 1 || isDefault) ? classes.modRemoved : classes.mod
    }
    return (
      <Button
        key={`${key}.${selected}.${item.qty}.${item.plu}.${isDefault}`}
        className={buttonClass}
        executeAction={() => sellFunc(item)}
      >
        {(!isDefault || item.isIngredient) && <div className={classes.modQty}>{item.qty}</div>}
        {item.text}
      </Button>
    )
  }

  render() {
    const { classes, className, expandCol } = this.props
    const { selectedModType } = this.state
    const renderInfo = this.renderInfo()
    const showMods = _.sum(renderInfo.colsNeededByGroup) > 0
    return (
      <div className={`${classes.container} ${className}`}>
        <div className={classes.title}>
          <I18N id="$MODIFIERS_TITLE" defaultMessage="Modifiers" />
        </div>
        {showMods &&
          <div className={classes.modsCont}>
            <div className={classes.modTypesBox}>
              {_.map(MOD_TYPES, (modType, idx) => {
                const selected = (selectedModType === idx)
                const selectedClass = (selected) ? classes.modTypeButtonSelected : ''
                return (
                  <Button
                    key={`${idx}_${selected}`}
                    style={styles.modTypeButton}
                    className={selectedClass}
                    rounded={true}
                    onClick={() => this.handleModTypeClick(idx)}
                  >
                    {modType.text}
                  </Button>
                )
              })}
            </div>
            <div className={classes.modGroupsBox}>
              <NavigationGrid
                groups={renderInfo.groups || []}
                sellFunc={this.handleSellModifier}
                onRenderSaleButton={this.handleRenderButton}
                cols={MAX_COLS}
                expandCol={expandCol}
                styleTitle={{
                  fontSize: '1.3vh',
                  color: 'black'
                }}
              />
            </div>
          </div>
        }
        {!showMods &&
          <center>
            <em className={classes.noMods}>
              <I18N id="$NO_MODIFIERS_PRODUCT" defaultMessage="No modifiers available for selected product"/>
            </em>
          </center>
        }
      </div>
    )
  }
}

Modifiers.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Custom class for main container
   */
  className: PropTypes.string,
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object.isRequired,
  /**
   * Modifiers from `modifiersReducer`
   */
  modifiers: PropTypes.object.isRequired,
  /**
   * Line to modify
   */
  saleLine: PropTypes.object.isRequired,
  /**
   * Called to by modifier screen to add a modifier
   */
  sellModifier: PropTypes.func,
  /**
   * Expand cols for modifiers
   */
  expandCol: PropTypes.number
}

Modifiers.defaultProps = {
  className: '',
  expandCol: MAX_COLS
}

export default injectSheet(styles)(Modifiers)
