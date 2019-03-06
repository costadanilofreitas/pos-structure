import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { NavigationGrid } from 'posui/widgets'
import _ from 'lodash'
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
  }
}

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
    const { sellOption, classes } = this.props
    const modifierGroup = this.getOptions()

    return (
      <div className={classes.container}>
        <div className={classes.title}>
          <I18N id="$OPTIONS_TITLE" defaultMessage="Options" />
        </div>
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
