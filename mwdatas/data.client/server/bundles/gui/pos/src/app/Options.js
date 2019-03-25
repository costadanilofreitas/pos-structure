import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import memoize from 'memoize-one'
import { NavigationGrid } from 'posui/widgets'
import { Button } from 'posui/button'
import injectSheet, { jss } from 'react-jss'
import { I18N } from 'posui/core'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  container: {
    width: '100%',
    height: '98%'
  },
  title: {
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: '4.5vh',
    position: 'relative'
  },
  optQty: {
    position: 'absolute',
    right: '2px',
    top: '2px'
  },
  opt: {
    fontSize: '1.4vh',
    backgroundColor: '#ffe082'
  }
}

class Options extends PureComponent {

  state = {
    selectedTabIdx: 0
  }

  getOptions() {
    const { selectedLine, modifiers } = this.props
    // get parent part code
    const productPartCode = _.split(selectedLine.itemId, '.')
    let parentPartCode = productPartCode.pop()
    const groups = []
    const isOption = (selectedLine || {}).itemType === 'OPTION'
    let optionPart
    let currentModifier
    let text
    let subst = ''
    let partCode = selectedLine.partCode
    if (isOption) {
      text = modifiers.descriptions[partCode]
      currentModifier = modifiers.modifiers[parentPartCode] || {}
      optionPart = currentModifier.parts[partCode]
    } else if (parentPartCode > 1) {
      subst = partCode
      partCode = parentPartCode
      text = modifiers.descriptions[parentPartCode]
      parentPartCode = productPartCode.pop()
      currentModifier = modifiers.modifiers[parentPartCode] || {}
      optionPart = currentModifier.parts[partCode]
      partCode = ''
    }
    if (optionPart) {
      const options = (optionPart.data || {}).options || []
      groups.push({
        text: null,
        classes: [],
        name: text,
        items: _.map(options, option => {
          return {
            text: modifiers.descriptions[option],
            plu: option,
            classes: [],
            bgColor: '#ffe082'
          }
        })
      })
    }
    return {
      itemId: `${selectedLine.itemId}.${partCode}`,
      subst,
      groups
    }
  }

  getOptQty = memoize((order, selectedLine) => {
    const optQty = {}
    let selectedLineLevel = parseFloat(selectedLine.level, 10)
    let foundLevel = null
    _.forEach(order.SaleLine || [], (line) => {
      const lineAttrs = line['@attributes'] || {}
      if (lineAttrs === selectedLine) {
        foundLevel = selectedLineLevel
      } else if (foundLevel !== null) {
        const level = parseFloat(lineAttrs.level, 10)
        if (level > foundLevel) {
          if (!_.has(optQty, lineAttrs.partCode)) {
            optQty[lineAttrs.partCode] = 0
          }
          optQty[lineAttrs.partCode] += parseInt(lineAttrs.qty, 10)
        } else {
          return false
        }
      }
      return true
    })
    return optQty
  })

  handleRenderButton = (optQty) => (item, key, sellFunc) => {
    const { classes } = this.props
    const selected = Boolean(item.selected)
    const qty = optQty[item.plu]

    return (
      <Button
        key={`${key}.${selected}.${item.qty}.${item.plu}`}
        className={classes.opt}
        executeAction={() => sellFunc(item)}
        blockOnActionRunning
        rounded
      >
        {(qty > 0) && <div className={classes.optQty}>{qty}</div>}
        {item.text}
      </Button>
    )
  }

  render() {
    const { sellOption, classes, order, selectedLine } = this.props
    const modifierGroup = this.getOptions()
    const optQty = this.getOptQty(order, selectedLine)

    return (
      <div className={classes.container}>
        <div className={classes.title}>
          <I18N id="$OPTIONS_TITLE" defaultMessage="Options" />
        </div>
        <NavigationGrid
          groups={modifierGroup.groups}
          sellFunc={(item) => sellOption(item, modifierGroup.itemId, modifierGroup.subst)}
          onRenderSaleButton={this.handleRenderButton(optQty)}
          cols={11}
          rows={11}
          maxSpanCols={11}
          expandCol={5}
          styleTitle={{
            fontSize: '1.3vh',
            color: 'black'
          }}
          buttonProps={{ blockOnActionRunning: true }}
        />
      </div>
    )
  }
}

Options.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object.isRequired,
  /**
   * Navigation state from `navigationReducer`
   */
  navigation: PropTypes.object,
  /**
   * Modifiers from `modifiersReducer`
   */
  modifiers: PropTypes.object,
  /**
   * SaleScreen selectedLine
   */
  selectedLine: PropTypes.object,
  /**
   * SaleScreen selectedParent
   */
  selectedParent: PropTypes.object,
  /**
   * Called to sell an option
   */
  sellOption: PropTypes.func
}

Options.defaultProps = {
  selectedLine: {},
  navigation: {},
  modifiers: {}
}

function mapStateToProps(state) {
  return {
    navigation: state.navigation,
    modifiers: state.modifiers
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(Options))
