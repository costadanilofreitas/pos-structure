import React from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle, CommonStyledButton } from '../../../../constants/commonStyles'
import OpenTabs from '../../../component/open-tabs'
import LogoutButton from '../../../component/logout-button'
import TablePlan from '../../../component/table-plan'
import TableList from '../../../component/table-list'
import TableWarns from '../../../component/table-warns'
import { TableStatus } from '../../../model/TableStatus'
import withGetMessage from '../../../../util/withGetMessage'
import withState from '../../../../util/withState'
import TableDetails from '../../../component/table-details'
import TablePropTypes from '../../../../prop-types/TablePropTypes'
import ButtonGrid from '../../../component/button-grid/ButtonGrid'


function DesktopTableListScreenRenderer(props) {
  const { classes, floorPlan, tableLists, showTableInfo, hasTables, selectedTable } = props
  const hasTablePlan = floorPlan.plan != null && Object.keys(floorPlan.plan).length > 0

  function tableInfo() {
    if (showTableInfo) {
      return (
        <FlexChild size={5}>
          {selectedTable != null ?
            <TableDetails selectedTable={props.selectedTable} compact={true}/> :
            <FlexGrid direction={'column'}>
              <FlexChild size={1} innerClassName={classes.titleContainer}>
                <I18N id={'$SELECT_TABLE'}/>
              </FlexChild>
              <FlexChild size={4}/>
            </FlexGrid>
          }
        </FlexChild>
      )
    }
    return null
  }

  function checkAndToggleTableInfo() {
    if (showTableInfo) {
      props.toggleTableInfo()
    }
  }

  function activateSearchButton() {
    checkAndToggleTableInfo()
    props.openTable()
  }

  const toggleFloorPlan = floorPlan.active && floorPlan.enabled && hasTablePlan ? 'fa-th' : 'fa-map'
  const toggleTableInfo = showTableInfo ? 'fa-toggle-on' : 'fa-toggle-off'
  const buttons = {
    0:
      <CommonStyledButton
        key={toggleTableInfo}
        executeAction={props.toggleTableInfo}
        active={showTableInfo}
        border={true}
      >
        <IconStyle className={`fas fa-2x ${toggleTableInfo}`} aria-hidden="true"/>
        <br/>
        <I18N id="$TABLE_INFO"/>
      </CommonStyledButton>,

    1:
      <OpenTabs checkAndToggleTableInfo={checkAndToggleTableInfo}/>,

    2:
      <CommonStyledButton
        className={'test_TableListScreenRenderer_SEARCH'}
        key={'openTable'}
        executeAction={() => activateSearchButton()}
        border={true}
      >
        <IconStyle className={'fas fa-2x fa-search'} aria-hidden="true"/>
        <br/>
        <I18N id="$SEARCH"/>
      </CommonStyledButton>,

    3:
      <CommonStyledButton
        className={`test_TableList_${toggleFloorPlan.toUpperCase()}`}
        key={toggleFloorPlan}
        executeAction={props.toggleLayout}
        disabled={!hasTables || !hasTablePlan || !floorPlan.enabled}
        border={true}
      >
        <IconStyle className={`fas fa-2x ${toggleFloorPlan}`} disabled={!hasTablePlan || !floorPlan.enabled} aria-hidden="true"/>
        <br/>
        {(floorPlan.active && hasTables && hasTablePlan) ? <I18N id="$TABLE_LIST"/> : <I18N id="$LAYOUT"/>}
      </CommonStyledButton>,

    4: <LogoutButton/>
  }

  const isFloorPlan = floorPlan.active && floorPlan.enabled && hasTables && hasTablePlan

  return (
    <FlexGrid>
      <FlexChild size={1} innerClassName={classes.tableListBackground}>
        <FlexGrid direction={'column'}>
          <FlexChild size={showTableInfo ? 7 : 12}>
            <TableWarns tables={tableLists[TableStatus.InProgress]} size={showTableInfo ? 7 : 12}/>
          </FlexChild>
          {tableInfo()}
          <FlexChild size={10}>
            <ButtonGrid direction="row" cols={1} rows={5} buttons={buttons} style={{ position: 'relative' }}/>
          </FlexChild>
        </FlexGrid>
      </FlexChild>
      <FlexChild size={5} innerClassName={classes.marginContainer}>
        {(isFloorPlan)
          ? <TablePlan tables={tableLists} executeTableClick={true}/>
          : <TableList tables={tableLists} hasTables={hasTables}/>
        }
      </FlexChild>
    </FlexGrid>
  )
}

DesktopTableListScreenRenderer.propTypes = {
  classes: PropTypes.object,
  tableLists: PropTypes.object,
  hasTables: PropTypes.bool,
  floorPlan: PropTypes.shape({
    active: PropTypes.bool,
    enabled: PropTypes.bool,
    rotation: PropTypes.number,
    plan: PropTypes.object
  }),
  showTableInfo: PropTypes.bool,
  selectedTable: TablePropTypes,
  toggleLayout: PropTypes.func,
  toggleTableInfo: PropTypes.func,
  openTable: PropTypes.func
}

export default withGetMessage(withState(DesktopTableListScreenRenderer, 'tableLists'))
