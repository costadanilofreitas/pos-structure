import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { connect } from 'react-redux'
import { I18N } from '3s-posui/core'
import { ensureDecimals } from '3s-posui/utils'
import { FlexChild, FlexGrid } from '3s-widgets'

import { CommonStyledButton } from '../../../constants/commonStyles'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import ActionButton from '../../../component/action-button/JssActionButton'
import DeviceType from '../../../constants/Devices'
import ButtonGrid from '../button-grid/ButtonGrid'


class TenderDivision extends Component {
  constructor(props) {
    super(props)

    const totalGross = ensureDecimals(Number((this.props.order['@attributes'] || {}).totalGross || '0'))
    const tenderLength = totalGross.length
    this.div2 = ensureDecimals(Math.ceil((totalGross * 100) / 2) / 100).padStart(tenderLength)
    this.div3 = ensureDecimals(Math.ceil((totalGross * 100) / 3) / 100).padStart(tenderLength)
    this.div4 = ensureDecimals(Math.ceil((totalGross * 100) / 4) / 100).padStart(tenderLength)
    this.div5 = ensureDecimals(Math.ceil((totalGross * 100) / 5) / 100).padStart(tenderLength)
  }

  getMaxNumPadValue(x) {
    const dueAmount = ensureDecimals(Number((this.props.order['@attributes'] || {}).dueAmount || '0'))
    return parseFloat(x) < parseFloat(dueAmount) ? x : dueAmount
  }

  render() {
    const { selectedTable, deviceType } = this.props

    if (deviceType === DeviceType.Totem) {
      return null
    }
    return selectedTable != null ? this.renderTable() : this.renderQuickService()
  }

  renderQuickService() {
    const { classes } = this.props

    const tenderDivision = {
      0:
        <CommonStyledButton
          onClick={() => this.props.setNumPadValue(this.getMaxNumPadValue(this.div2))}
          border={true}
        >
          <div className={classes.bigTenderDivText}>
          DIV 2: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div2}
          </div>
        </CommonStyledButton>,
      1:
        <CommonStyledButton
          onClick={() => this.props.setNumPadValue(this.getMaxNumPadValue(this.div3))}
          border={true}
        >
          <div className={classes.bigTenderDivText}>
          DIV 3: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div3}
          </div>
        </CommonStyledButton>,
      2:
        <CommonStyledButton
          onClick={() => this.props.setNumPadValue(this.getMaxNumPadValue(this.div4))}
          border={true}
        >
          <div className={classes.bigTenderDivText}>
          DIV 4: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div4}
          </div>
        </CommonStyledButton>,
      3:
        <CommonStyledButton
          onClick={() => this.props.setNumPadValue(this.getMaxNumPadValue(this.div5))}
          border={true}
        >
          <div className={classes.bigTenderDivText}>
          DIV 5: <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {this.div5}
          </div>
        </CommonStyledButton>
    }

    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={1} innerClassName={classes.titleContainer}>
          <I18N id={'$TENDER_DIVISION'}/>
        </FlexChild>
        <FlexChild size={2}>
          <ButtonGrid direction="column" cols={2} rows={2} buttons={tenderDivision}/>
        </FlexChild>
      </FlexGrid>
    )
  }

  renderTable() {
    const { classes } = this.props
    const totalGross = ensureDecimals(Number((this.props.order['@attributes'] || {}).totalGross || '0'))

    const divisionPerSeat = (Math.ceil((totalGross * 100) / 5) / 100).padStart(this.props.selectedTable.serviceSeats)
    const divisionValue = ensureDecimals(divisionPerSeat)

    return (
      <FlexGrid>
        <FlexChild>
          <I18N id={'$TENDER_DIVISION'}/>
        </FlexChild>
        <FlexChild>
          <ActionButton
            onClick={() => this.props.setNumPadValue(divisionValue)}
          >
            <div className={classes.bigTenderDivText}>
              <I18N id="$L10N_CURRENCY_SYMBOL" defaultMessage="$" /> {divisionValue}
            </div>
          </ActionButton>
        </FlexChild>
      </FlexGrid>
    )
  }
}

TenderDivision.propTypes = {
  classes: PropTypes.object,
  setNumPadValue: PropTypes.func,
  order: PropTypes.object,
  selectedTable: TablePropTypes,
  deviceType: PropTypes.number
}

TenderDivision.defaultProps = {
  order: {},
  custom: {}
}

function mapStateToProps(state) {
  return {
    order: state.order,
    custom: state.custom,
    workingMode: state.workingMode,
    deviceType: state.deviceType
  }
}

export default connect(mapStateToProps, null)(TenderDivision)
