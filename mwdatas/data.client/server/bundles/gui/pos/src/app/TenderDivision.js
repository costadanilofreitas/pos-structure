import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { I18N } from 'posui/core'
import { Button } from 'posui/button'
import { ButtonGrid, SaleTypeSelector, NumPad } from 'posui/widgets'
import { SalePanel } from 'posui/sale-panel'
import { ensureDecimals } from 'posui/utils'
import injectSheet, { jss } from 'react-jss'
import setMenuAction from '../actions/setMenuAction'
import {DataTable, ScrollPanel} from "./RecallScreen";

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  bigTenderDivText: {
    fontSize: '2vh',
    whiteSpace: 'pre'
  },
  tenderDivGrid: {
    padding: '0.1vh'
  },
}

class TenderDivision extends PureComponent {
  constructor(props) {
    super(props)

    const totalGross = ensureDecimals(Number((this.props.order['@attributes'] || {}).totalGross || '0'))
    const tenderLength = totalGross.length
    this.div2 = ensureDecimals(Math.ceil(totalGross * 100 / 2) / 100).padStart(tenderLength)
    this.div3 = ensureDecimals(Math.ceil(totalGross * 100 / 3) / 100).padStart(tenderLength)
    this.div4 = ensureDecimals(Math.ceil(totalGross * 100 / 4) / 100).padStart(tenderLength)
    this.div5 = ensureDecimals(Math.ceil(totalGross * 100 / 5) / 100).padStart(tenderLength)
  }

  getMaxNumPadValue(x) {
    const dueAmount = ensureDecimals(Number((this.props.order['@attributes'] || {}).dueAmount || '0'))
    return parseFloat(x) < parseFloat(dueAmount) ? x : dueAmount
  }

  render() {
    const tenderDivision = {
      0: <Button
           executeAction={() => { this.props.setNumPadValue(this.getMaxNumPadValue(this.div2)) }}>
          <div style={styles.bigTenderDivText}>
           DIV 2: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div2}
          </div>
         </Button>,
      1: <Button
           executeAction={() => { this.props.setNumPadValue(this.getMaxNumPadValue(this.div3)) }}>
          <div style={styles.bigTenderDivText}>
           DIV 3: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div3}
          </div>
         </Button>,
      2: <Button
           executeAction={() => { this.props.setNumPadValue(this.getMaxNumPadValue(this.div4)) }}>
          <div style={styles.bigTenderDivText}>
           DIV 4: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div4}
          </div>
         </Button>,
      3: <Button
           executeAction={() => { this.props.setNumPadValue(this.getMaxNumPadValue(this.div5)) }}>
           <div style={styles.bigTenderDivText}>
           DIV 5: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div5}
          </div>
         </Button>
    }

    return (
      <ButtonGrid
        styleCell={styles.tenderDivGrid}
        direction="column"
        cols={2}
        rows={2}
        buttons={tenderDivision}
        style={{ height: this.props.style.height, position: 'relative' }}
      />
    )
  }
}

TenderDivision.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * @ignore
   */
  setNumPadValue: PropTypes.func,
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object,
  /**
   * Order state from `orderReducer`
   */
  style: PropTypes.shape({height:PropTypes.string.required}),
}

TenderDivision.defaultProps = {
  order: {},
  custom: {}
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setMenu: setMenuAction
  }, dispatch)
}

function mapStateToProps(state) {
  return {
    order: state.order,
    custom: state.custom
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(TenderDivision))
