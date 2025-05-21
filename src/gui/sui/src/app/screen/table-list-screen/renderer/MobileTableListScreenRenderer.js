import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle } from '../../../../constants/commonStyles'
import FilterListBox from '../../../../component/filter-listbox'
import LogoutButton from '../../../component/logout-button'
import ActionButton from '../../../../component/action-button'
import OpenTabs from '../../../component/open-tabs'
import withGetMessage from '../../../../util/withGetMessage'
import { getStatusLabel } from '../../../model/TableStatus'
import withState from '../../../../util/withState'
import DailyGoals from '../../../component/daily-goals'
import OperatorPropTypes from '../../../../prop-types/OperatorPropTypes'
import { isCashierFunction, isOrderTakerFunction } from '../../../model/modelHelper'


class MobileTableListScreenRenderer extends Component {
  constructor(props) {
    super(props)

    const filteredTableList = MobileTableListScreenRenderer.filterTableList(props)
    this.state = {
      chosenValue: undefined,
      filteredTableList: filteredTableList
    }

    this.tableInfoLabel = this.tableInfoLabel.bind(this)
    this.buildTablesList = this.buildTablesList.bind(this)
    this.setValue = this.setValue.bind(this)
    this.openTable = this.openTable.bind(this)
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const filterTableList = MobileTableListScreenRenderer.filterTableList(nextProps)
    return {
      chosenValue: filterTableList.length === 0 ? undefined : prevState.chosenValue,
      filteredTableList: filterTableList
    }
  }

  static filterTableList(props) {
    const filteredTableList = []
    const tablesAndTabs = props.tableLists.tabs.concat(props.tableLists[0])
    _.map(tablesAndTabs, (tableItem) => {
      if (isCashierFunction(props.workingMode)) {
        if (tableItem.statusDescr === 'InProgress' || tableItem.statusDescr === 'Totaled') {
          filteredTableList.push(tableItem)
        }
      } else if (isOrderTakerFunction(props.workingMode)) {
        if (tableItem.statusDescr !== 'Totaled') {
          filteredTableList.push(tableItem)
        }
      } else {
        filteredTableList.push(tableItem)
      }
    })

    filteredTableList.sort((first, second) => second.status - first.status)
    return filteredTableList
  }

  tableInfoLabel(tableItem) {
    const { getMessage } = this.props
    function getStatus(status) {
      const label = getStatusLabel(status)
      return getMessage(label)
    }

    if (tableItem.tabId === '') {
      return `${getMessage('$TABLE')} ${tableItem.id} - ${getStatus(tableItem.status)}`
    }
    return `${getMessage('$TAB_NUMBER')} ${tableItem.tabId} - ${getStatus(tableItem.status)}`
  }

  setValue(value) {
    this.setState({ chosenValue: value })
  }

  openTable() {
    const { filteredTableList, chosenValue } = this.state
    const { openTable } = this.props
    const allValues = this.buildTablesList()

    if (chosenValue == null) {
      return
    }

    const index = allValues.indexOf(chosenValue)
    const tableId = filteredTableList[index].id
    openTable(tableId)
  }

  buildTablesList() {
    return _.map(this.state.filteredTableList, (tableItem) => {
      return this.tableInfoLabel(tableItem)
    })
  }

  render() {
    const { chosenValue } = this.state
    const { classes, operator } = this.props
    const allValues = this.buildTablesList()

    return (
      <div className={classes.absoluteWrapper}>
        <div className={classes.tableListBackground}>
          <FlexGrid direction={'column'}>
            <FlexChild size={2}>
              <div className={classes.goalsContainer}>
                <DailyGoals
                  showAmountChart={false}
                  showItemsChart={false}
                  showOperatorsTable={false}
                  showAverageTicketChart={true}
                  showSubtitles={true}
                  showInAllScreen={true}
                  goalsFlexDirection={'column'}
                  selectedOperator={operator.id}
                />
              </div>
            </FlexChild>
            <FlexChild size={8}>
              <FilterListBox
                allValues={allValues}
                setFilteredValue={(value) => this.setValue(value)}
                showFilter={true}
                direction={'column'}
                scrollY={true}
              />
            </FlexChild>
            <FlexChild size={1}>
              <FlexGrid direction={'row'}>
                <FlexChild>
                  <LogoutButton/>
                </FlexChild>
                <FlexChild>
                  <OpenTabs/>
                </FlexChild>
                <FlexChild>
                  <ActionButton
                    className={'test_TableList_OPEN-TABLE'}
                    key={'openTable'}
                    executeAction={this.openTable}
                    disabled={chosenValue == null}
                  >
                    <IconStyle className={'fas fa-play fa-2x'} aria-hidden="true"/><br/>
                    <I18N id="$OPEN_TABLE"/>
                  </ActionButton>
                </FlexChild>
              </FlexGrid>
            </FlexChild>
          </FlexGrid>
        </div>
      </div>
    )
  }
}

const table = PropTypes.shape({
  id: PropTypes.string.isRequired,
  status: PropTypes.number.isRequired,
  tabId: PropTypes.string
})

MobileTableListScreenRenderer.propTypes = {
  classes: PropTypes.object,
  tableLists: PropTypes.shape({
    all: PropTypes.arrayOf(table),
    tabs: PropTypes.arrayOf(table)
  }),
  openTable: PropTypes.func,
  getMessage: PropTypes.func,
  operator: OperatorPropTypes
}


export default withGetMessage(withState(MobileTableListScreenRenderer, 'tableLists', 'operator', 'workingMode'))
