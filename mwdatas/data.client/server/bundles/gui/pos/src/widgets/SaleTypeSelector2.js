import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { I18N } from 'posui/core'
import { Button } from 'posui/button'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  saleTypeSelectorRoot: {
    composes: 'sale-type-selector-root',
    width: '100%',
    height: '100%'
  },
  saleTypeSelectorCont: {
    composes: 'sale-type-selector-cont',
    fontWeight: 'bold',
    width: '100%',
    height: '100%',
    boxSizing: 'border-box',
    display: 'flex'
  },
  saleTypeSelectorContRow: {
    composes: 'sale-type-selector-cont-row',
    flexDirection: 'row'
  },
  saleTypeSelectorContColumn: {
    composes: 'sale-type-selector-cont-column',
    flexDirection: 'column'
  },
  saleTypeSelectorButton: {
    composes: 'sale-type-selector-button',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  saleTypeSelectorButtonColumn: {
    composes: 'sale-type-selector-button-column',
    height: '50%'
  },
  saleTypeSelectorButtonRow: {
    composes: 'sale-type-selector-button-row',
    height: '100%'
  },
  saleTypeSelectorButtonEatIn: {
    composes: 'sale-type-selector-button-eat-in'
  },
  saleTypeSelectorButtonEatInBorderColumn: {
    composes: 'sale-type-selector-button-eat-in-border-column',
    borderTop: '1px solid #cccccc',
    borderLeft: '1px solid #cccccc',
    borderRight: '1px solid #cccccc'
  },
  saleTypeSelectorButtonEatInRoundedColumn: {
    composes: 'sale-type-selector-button-eat-in-rounded-column',
    borderRadius: '5px 5px 0 0'
  },
  saleTypeSelectorButtonEatInBorderRow: {
    composes: 'sale-type-selector-button-eat-in-border-row',
    borderTop: '1px solid #cccccc',
    borderLeft: '1px solid #cccccc',
    borderBottom: '1px solid #cccccc'
  },
  saleTypeSelectorButtonEatInRoundedRow: {
    composes: 'sale-type-selector-button-eat-in-rounded-row',
    borderRadius: '5px 0 0 5px'
  },
  saleTypeSelectorButtonTakeOut: {
    composes: 'sale-type-selector-button-take-out'
  },
  saleTypeSelectorButtonTakeOutBorderColumn: {
    composes: 'sale-type-selector-button-take-out-border-column',
    borderBottom: '1px solid #cccccc',
    borderLeft: '1px solid #cccccc',
    borderRight: '1px solid #cccccc'
  },
  saleTypeSelectorButtonTakeOutRoundedColumn: {
    composes: 'sale-type-selector-button-take-out-rounded-column',
    borderRadius: '0 0 5px 5px'
  },
  saleTypeSelectorButtonTakeOutBorderRow: {
    composes: 'sale-type-selector-button-take-out-border-row',
    borderBottom: '1px solid #cccccc',
    borderTop: '1px solid #cccccc',
    borderRight: '1px solid #cccccc'
  },
  saleTypeSelectorButtonTakeOutRoundedRow: {
    composes: 'sale-type-selector-button-take-out-rounded-row',
    borderRadius: '0 5px 5px 0'
  },
  saleTypeSelectorIcon: {
    composes: 'sale-type-selector-icon fa fa-check',
    width: '20%',
    height: '100%',
    display: 'flex !important',
    alignItems: 'center',
    justifyContent: 'center'
  },
  saleTypeSelectorText: {
    composes: 'sale-type-selector-text',
    width: '80%',
    height: '100%',
    alignItems: 'center',
    display: 'flex',
    fontSize: '1.8vh'
  },
  saleTypeSelectorEatInSelected: {
    composes: 'sale-type-selector-eat-in-selected',
    backgroundColor: '#43A047 !important',
    color: 'white !important'
  },
  saleTypeSelectorTakeOutSelected: {
    composes: 'sale-type-selector-take-out-selected',
    backgroundColor: '#EF5350 !important',
    color: 'white !important'
  },
  saleTypeSelectorUnselected: {
    composes: 'sale-type-selector-unselected',
    backgroundColor: 'white !important',
    color: 'black !important',
    '& i.sale-type-selector-icon': {
      color: '#F2F2F2'
    }
  }
}

const ST_EAT_IN = '$EAT_IN'
const ST_TAKE_OUT = '$TAKE_OUT'

/**
 * This widget is a basic button toggle to change current sale's type, between 'Eat in' and
 * 'Take out'.
 *
 * In order to use this component, your app state must expose the following states:
 * - `order` using `orderReducer` reducer
 *
 * Available class names:
 * - root element: `sale-type-selector-root`
 * - container element: `sale-type-selector-cont`
 * - container when direction is column: sale-type-selector-cont-column`
 * - container when direction is row: sale-type-selector-cont-row`
 * - button elements: `sale-type-selector-button`
 * - button when direction is column: `sale-type-selector-button-column`
 * - button when direction is row: `sale-type-selector-button-row`
 * - eat-in button element: `sale-type-selector-button-eat-in`
 * - eat-in button when border and column: `sale-type-selector-button-eat-in-border-column`
 * - eat-in button when border and row: `sale-type-selector-button-eat-in-border-row`
 * - eat-in button when rounded and column: `sale-type-selector-button-eat-in-rounded-column`
 * - eat-in button when rounded and row: `sale-type-selector-button-eat-in-rounded-row`
 * - take-out button element: `sale-type-selector-button-take-out`
 * - take-out button when border and column: `sale-type-selector-button-take-out-border-column`
 * - take-out button when border and row: `sale-type-selector-button-take-out-border-row`
 * - take-out button when rounded and column: `sale-type-selector-button-take-out-rounded-column`
 * - take-out button when rounded and row: `sale-type-selector-button-take-out-rounded-row`
 * - button icon elements: `sale-type-selector-icon`
 * - button text elements: `sale-type-selector-text`
 * - eat-in button selected element: `sale-type-selector-eat-in-selected`
 * - take-out button selected element: `sale-type-selector-take-out-selected`
 * - unselected button elements: `sale-type-selector-unselected`
 */


class SalePanelHeader2 extends PureComponent {

  render() {
    const {
      classes, style, styleCont, styleButton, styleButtonEatIn, styleButtonTakeOut,
      styleUnselected, styleEatInSelected, styleTakeOutSelected, styleIcon, styleText, rounded,
      direction, border, changeType, orderType
    } = this.props
    const saleType = orderType
    const topClass = (saleType ? classes.saleTypeSelectorEatInSelected : classes.saleTypeSelectorUnselected)
    const bottomClass = (saleType ? classes.saleTypeSelectorUnselected : classes.saleTypeSelectorTakeOutSelected)
    const row = (direction === 'row')
    let topRound = ''
    let bottomRound = ''
    if (rounded) {
      if (row) {
        topRound = classes.saleTypeSelectorButtonEatInRoundedRow
        bottomRound = classes.saleTypeSelectorButtonTakeOutRoundedRow
      } else {
        topRound = classes.saleTypeSelectorButtonEatInRoundedColumn
        bottomRound = classes.saleTypeSelectorButtonTakeOutRoundedColumn
      }
    }
    let topBorder = ''
    let bottomBorder = ''
    if (border) {
      if (row) {
        topBorder = classes.saleTypeSelectorButtonEatInBorderRow
        bottomBorder = classes.saleTypeSelectorButtonTakeOutBorderRow
      } else {
        topBorder = classes.saleTypeSelectorButtonEatInBorderColumn
        bottomBorder = classes.saleTypeSelectorButtonTakeOutBorderColumn
      }
    }
    const contClass = (row) ?
      classes.saleTypeSelectorContRow : classes.saleTypeSelectorContColumn
    const buttonClass = (row) ?
      classes.saleTypeSelectorButtonRow : classes.saleTypeSelectorButtonColumn
    return (
      <div className={classes.saleTypeSelectorRoot} style={style}>
        <div className={`${classes.saleTypeSelectorCont} ${contClass}`} style={styleCont}>
          <Button
            style={{ ...styleButton, ...styleButtonEatIn, ...(saleType ? styleEatInSelected : styleUnselected) }}
            className={`${classes.saleTypeSelectorButton} ${buttonClass} ${classes.saleTypeSelectorButtonEatIn} ${topBorder} ${topRound} ${topClass}`}
             onClick={changeType}>
            <i className={classes.saleTypeSelectorIcon} style={styleIcon}></i>
            <div key={ST_EAT_IN} className={classes.saleTypeSelectorText} style={styleText}>
              <I18N id={ST_EAT_IN} defaultMessage="Eat-in" />
            </div>
          </Button>
          <Button
            style={{ ...styleButton, ...styleButtonTakeOut, ...(saleType ? styleUnselected : styleTakeOutSelected) }}
            className={`${classes.saleTypeSelectorButton} ${buttonClass} ${classes.saleTypeSelectorButtonTakeOut} ${bottomBorder} ${bottomRound} ${bottomClass}`}
             onClick={changeType}>
            <i className={classes.saleTypeSelectorIcon} style={styleIcon}></i>
            <div key={ST_TAKE_OUT} className={classes.saleTypeSelectorText} style={styleText}>
              <I18N id={ST_TAKE_OUT} defaultMessage="Take-out" />
            </div>
          </Button>
        </div>
      </div>
    )
  }
}

SalePanelHeader2.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Component's root style override
   */
  style: PropTypes.object,
  /**
   * Component's container style override
   */
  styleCont: PropTypes.object,
  /**
   * Component's button style override, for both 'Eat in' and 'Take out' buttons
   */
  styleButton: PropTypes.object,
  /**
   * Component's 'Eat in' button style override
   */
  styleButtonEatIn: PropTypes.object,
  /**
   * Component's 'Take out' button style override
   */
  styleButtonTakeOut: PropTypes.object,
  /**
   * Component's 'Eat in' button selected style override
   */
  styleEatInSelected: PropTypes.object,
  /**
   * Component's 'Take out' button selected style override
   */
  styleTakeOutSelected: PropTypes.object,
  /**
   * Component's button unselected style override, for both 'Eat in' and 'Take out' buttons
   */
  styleUnselected: PropTypes.object,
  /**
   * Component's button icon style override
   */
  styleIcon: PropTypes.object,
  /**
   * Component's button text style override
   */
  styleText: PropTypes.object,
  /**
   * Order state from `orderReducer`
   * @ignore
   */
  order: PropTypes.object,
  /**
   * Use default border on the component
   */
  border: PropTypes.bool,
  /**
   * Use rounded corners on the component
   */
  rounded: PropTypes.bool,

  orderType: PropTypes.bool,

  changeType: PropTypes.func,
  /**
   * Buttons orientation, valid options are: 'row', 'column'
   */
  direction: PropTypes.oneOf(['row', 'column'])
}

SalePanelHeader2.defaultProps = {
  order: {},
  style: {},
  styleCont: {},
  styleButton: {},
  styleButtonEatIn: {},
  styleButtonTakeOut: {},
  styleEatInSelected: {},
  styleTakeOutSelected: {},
  styleUnselected: {},
  styleIcon: {},
  styleText: {},
  border: true,
  rounded: true,
  direction: 'column'
}

function mapStateToProps(state) {
  return {
    order: state.order

  }
}

export default connect(mapStateToProps)(injectSheet(styles)(SalePanelHeader2))
