import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { TableStatus } from '../../../model/TableStatus'
import withState from '../../../../util/withState'
import WorkingModePropTypes from '../../../../prop-types/WorkingModePropTypes'
import { isCashierFunction, isOrderTakerFunction } from '../../../model/modelHelper'
import { ContainerStyle, ButtonStyle } from './StyledTableStateFilter'
import { ArrowUp, ArrowUpContainer } from '../../buttons/common/StyledCommonRenderer'

class TableStateFilter extends Component {
  render() {
    const { currentFilter, workingMode, hasTables } = this.props
    const statusList = this.initializeStatusList(workingMode, hasTables)

    return (
      <ContainerStyle>
        {statusList.map((status) => {
          const selected = status.value === currentFilter
          const classTest = `test_TableStateFilter_${status.label.toUpperCase().slice(1)}`
          return (
            <ButtonStyle
              status={status.key}
              key={`${status.key}.${selected}`}
              className={`${selected} ${classTest}`}
              onClick={() => this.handleClick(status)}
              text={status.label}
              blockOnActionRunning={true}
              selected={selected}
            >
              {selected && <ArrowUpContainer><ArrowUp/></ArrowUpContainer>}
            </ButtonStyle>
          )
        })}
      </ContainerStyle>
    )
  }

  initializeStatusList(workingMode, hasTables) {
    const statusList = []

    if (hasTables) {
      if (!isCashierFunction(workingMode)) {
        statusList.push({ key: 'all', label: '$ALL', value: 0, menuId: 0 })
        statusList.push({ key: 'available', label: '$AVAILABLE', value: TableStatus.Available, menuId: 1 })
      }

      statusList.push({ key: 'inProgress', label: '$IN_PROGRESS', value: TableStatus.InProgress, menuId: 2 })

      if (!isOrderTakerFunction(workingMode)) {
        statusList.push({ key: 'totaled', label: '$TOTALED', value: TableStatus.Totalized, menuId: 3 })
      }

      if (!isCashierFunction(workingMode)) {
        statusList.push({ key: 'closed', label: '$CLOSED', value: TableStatus.Closed, menuId: 4 })
      }
    }

    if (this.props.enableTabBtns) {
      statusList.push({ key: 'tabs', label: '$TABS', value: 'tabs', menuId: 5 })
    }

    return statusList
  }

  handleClick(status) {
    this.props.onFilterChange(status.value)
  }
}

TableStateFilter.propTypes = {
  classes: PropTypes.object.isRequired,
  workingMode: WorkingModePropTypes,
  hasTables: PropTypes.bool,
  onFilterChange: PropTypes.func,
  currentFilter: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  enableTabBtns: PropTypes.bool
}

export default withState(TableStateFilter, 'workingMode')
