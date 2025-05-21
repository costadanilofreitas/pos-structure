import React, { Component } from 'react'
import PropTypes from 'prop-types'

import TenderScreenRenderer from './tender-screen-renderer'
import TableDetails from '../../component/table-details'
import TableActions from '../../component/table-actions'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import OrderTotal from '../../component/order-total'
import OrderTenders from '../../component/order-tenders'
import CustomSalePanel from '../../component/custom-sale-panel'
import TenderDivision from '../../component/tender-division'
import MessageBusPropTypes from '../../../prop-types/MessageBusPropTypes'
import OrderPropTypes from '../../../prop-types/OrderPropTypes'
import OrderFunctions from '../../component/order-functions'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'


export default class TenderScreen extends Component {
  constructor(props) {
    super(props)

    this.state = {
      selectedTenderDivisionValue: '0',
      isSalePanelVisible: false
    }

    this.setNumPadValue = this.setNumPadValue.bind(this)
    this.handleOnToggleSalePanel = this.handleOnToggleSalePanel.bind(this)
  }

  render() {
    const { selectedTable, tefAvailable } = this.props
    const { selectedTenderDivisionValue } = this.state

    return (
      <TenderScreenRenderer
        msgBus={this.props.msgBus}
        staticConfig={this.props.staticConfig}
        order={this.props.order}
        customOrder={this.props.customOrder}
        toggleTenderScreen={this.props.toggleTenderScreen}
      >
        <TableDetails selectedTable={selectedTable}/>
        <OrderTenders
          showTef={tefAvailable}
          selectedTenderDivisionValue={selectedTenderDivisionValue}
          setNumPadValue={this.setNumPadValue}
        />
        <OrderTotal
          onToggleSalePanel={this.handleOnToggleSalePanel}
          isSalePanelVisible={this.state.isSalePanelVisible}
          onLineClick={() => {}}
        />
        <TableActions selectedTable={this.props.selectedTable}/>
        <OrderFunctions/>
        <CustomSalePanel/>
        <TenderDivision selectedTable={selectedTable} setNumPadValue={this.setNumPadValue}/>
      </TenderScreenRenderer>)
  }

  setNumPadValue(selectedTenderDivisionValue) {
    this.setState({ selectedTenderDivisionValue })
  }

  handleOnToggleSalePanel() {
    this.setState({ isSalePanelVisible: !this.state.isSalePanelVisible })
  }
}

TenderScreen.propTypes = {
  selectedTable: TablePropTypes,
  tefAvailable: PropTypes.bool,
  msgBus: MessageBusPropTypes,
  order: OrderPropTypes,
  staticConfig: StaticConfigPropTypes,
  customOrder: OrderPropTypes,
  toggleTenderScreen: PropTypes.func
}
