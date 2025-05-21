import React, { Component } from 'react'
import PropTypes from 'prop-types'
import injectSheet from 'react-jss'
import { utcTimeNow, showAlert } from '../../../../../util/timeFunctions'
import StaticConfigPropTypes from '../../../../../prop-types/StaticConfigPropTypes'
import { StyledButton, ButtonIcon, ButtonText } from './StyledTableItem'


const styles = (theme) => ({
  alertIsIdle: {
    backgroundColor: `${theme.tableFillIdle} !important`,
    color: `${theme.screenBackground} !important`
  },
  alertIsIdleWarning: {
    backgroundColor: `${theme.tableFillIdleWarning} !important`
  },
  alertLinked: {
    backgroundColor: `${theme.tableFillLinked} !important`
  }
})

class TableItem extends Component {
  constructor(props) {
    super(props)

    this.interval = null
    this.state = {
      time: utcTimeNow()
    }
  }

  render() {
    const { classes } = this.props
    const alertIsIdle = this.props.staticConfig.timeToAlertTableIsIdle
    const alertIsIdleWarning = this.props.staticConfig.timeToAlertTableIsIdleWarning

    let buttonClass = ''

    if (this.props.statusDescr === 'Linked') {
      buttonClass += ` ${classes.alertLinked}`
    } else if (this.props.statusDescr !== 'Available' && this.props.statusDescr !== 'Totaled') {
      if (showAlert(this.props.lastUpdateTS, this.state.time, alertIsIdle)) {
        buttonClass += ` ${classes.alertIsIdle}`
      } else if (showAlert(this.props.lastUpdateTS, this.state.time, alertIsIdleWarning)) {
        buttonClass += ` ${classes.alertIsIdleWarning}`
      }
    }

    return (
      <StyledButton
        onClick={() => this.props.onTableClick(this.props)}
        className={this.props.tabId !== ''
          ? `${buttonClass} test_TableItem_TAB`
          : `${buttonClass} test_TableItem_TABLE`}
        blockOnActionRunning
      >
        <ButtonIcon>
          {this.props.tabId !== '' ? <i className="fas fa-pager fa-2x" aria-hidden="true"/> :
            <i className="fas fa-utensils fa-2x" aria-hidden="true"/>}
        </ButtonIcon>
        <ButtonText>
          {this.props.tabId !== '' ? this.props.tabId : this.props.id}
        </ButtonText>
      </StyledButton>
    )
  }

  componentDidMount() {
    this.interval = setInterval(() => {
      this.setState({ time: utcTimeNow() })
    }, 1000)
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }
}

TableItem.propTypes = {
  classes: PropTypes.object.isRequired,
  id: PropTypes.string.isRequired,
  tabId: PropTypes.string,
  onTableClick: PropTypes.func.isRequired,
  lastUpdateTS: PropTypes.string,
  staticConfig: StaticConfigPropTypes,
  statusDescr: PropTypes.string
}

export default injectSheet(styles)(TableItem)
