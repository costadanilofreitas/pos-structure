import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { NavigationGrid } from 'posui/widgets'
import _ from 'lodash'

class Options extends PureComponent {

  state = {
    selectedTabIdx: 0
  }

  getOptions() {
    const { selectedLine, modifiers } = this.props
    // get parent part code
    const parentPartCode = _.last(_.split(selectedLine.itemId, '.'))
    const currentModifier = modifiers.modifiers[parentPartCode] || {}
    let groups = []
    let partCode = selectedLine.partCode
    const optionPart = currentModifier.parts[partCode]
    const text = modifiers.descriptions[partCode]
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
      groups
    }
  }

  render() {
    const { sellOption } = this.props
    const modifierGroup = this.getOptions()

    return (
      <NavigationGrid
        groups={modifierGroup.groups}
        sellFunc={(item) => sellOption(item, modifierGroup.itemId)}
        cols={11}
        rows={11}
        maxSpanCols={11}
        expandCol={7}
        styleTitle={{
          fontSize: '1.3vh',
          color: 'black'
        }}
      />
    )
  }
}

Options.propTypes = {
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

export default connect(mapStateToProps)(Options)
