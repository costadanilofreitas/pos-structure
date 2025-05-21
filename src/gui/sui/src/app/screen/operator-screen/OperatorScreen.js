import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { I18N } from '3s-posui/core'

import withChangeMenu from '../../util/withChangeMenu'
import Button from '../../../component/action-button/Button'
import ButtonGrid from '../../component/button-grid/ButtonGrid'

const styles = {
  container: {
    display: 'flex',
    width: '100%',
    height: '100%',
    position: 'absolute'
  },
  buttonsGroup: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative',
    margin: '0.5vw',
    background: 'rgb(255, 255, 255)'
  },
  gridPadding: {
    padding: '1px'
  },
  pinkBtn: {
    backgroundColor: '#FF3D72',
    color: '#ffffff'
  },
  blueBtn: {
    backgroundColor: '#3D73CC',
    color: '#ffffff'
  }
}

const FunctionButton = (props) => (
  <Button className="function-btn" blockOnActionRunning {...props}/>
)

export class OperatorScreen extends PureComponent {
  constructor(props) {
    super(props)

    this.handleOnOperatorClose = this.handleOnOperatorClose.bind(this)
  }

  handleOnOperatorClose(response) {
    if (response.data.toLowerCase() === 'true') {
      this.props.changeMenu(null)
    }
  }

  getOperatorButtons() {
    const { operator } = this.props

    return {
      0:
        <FunctionButton
          className={'test_OperatorScreen_CLOSE-USER'}
          style={styles.pinkBtn}
          executeAction={['common_logoff']}
          onActionFinish={(response) => this.handleOnOperatorClose(response)}
        >
          <I18N id="$CLOSE_USER"/>
        </FunctionButton>,

      21:
        <FunctionButton
          className={'test_OperatorScreen_SALES-BUSINESS'}
          style={styles.blueBtn}
          executeAction={['cashReport', 'current', 'BusinessPeriod', 'notAsk', 'True', '', 'True']}
        >
          <I18N id="$RESTAURANT_SALES_BUSINESS_PERIOD"/>
        </FunctionButton>,

      22:
        <FunctionButton
          className={'test_OperatorScreen_TIP-REPORT'}
          style={styles.blueBtn}
          executeAction={['tipReport', 'notAsk', 'True']}
        >
          <I18N id="$TIP_REPORT" defaultMessage="Tip Report"/>
        </FunctionButton>,

      23:
        <FunctionButton
          className={'test_OperatorScreen_MIX-BUSINESS'}
          style={styles.blueBtn}
          executeAction={['productMixReportByPeriod', 'BusinessPeriod', 'notAsk', 'notAsk', 'True']}
        >
          <I18N id="$PRODUCT_MIX_BUSINESS_PERIOD"/>
        </FunctionButton>,

      24:
        <FunctionButton
          className={'test_OperatorScreen_INTERVAL-SALES'}
          style={styles.blueBtn}
          executeAction={['hourlySalesReport', 'ask', 'notAsk', 'True']}
        >
          <I18N id="$INTERVAL_SALES"/>
        </FunctionButton>,

      27:
        <FunctionButton
          className={'test_OperatorScreen_DAILY-GOAL'}
          style={styles.blueBtn}
          executeAction={['show_daily_goals', operator.id, 'True', 'True', 'False', 'True']}
        >
          <I18N id="$DAILY_GOALS"/>
        </FunctionButton>,

      28:
        <FunctionButton
          className={'test_OperatorScreen_OPERATOR-CLOSING'}
          style={styles.blueBtn}
          executeAction={['show_operator_closing', operator.id]}
        >
          <I18N id="$OPERATOR_CLOSING"/>
        </FunctionButton>
    }
  }

  render() {
    const buttons = this.getOperatorButtons()

    return (
      <div style={styles.container}>
        <div style={styles.buttonsGroup}>
          <ButtonGrid
            styleCell={styles.gridPadding}
            direction="column"
            cols={5}
            rows={7}
            buttons={buttons}
          />
        </div>
      </div>
    )
  }
}

OperatorScreen.propTypes = {
  changeMenu: PropTypes.func,
  operator: PropTypes.object
}

OperatorScreen.defaultProps = {
  custom: {}
}

function mapStateToProps({ custom }) {
  return {
    custom
  }
}

export default withChangeMenu(connect(mapStateToProps)(OperatorScreen))
