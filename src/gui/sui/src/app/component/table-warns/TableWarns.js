import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'
import { I18N } from '3s-posui/core'

import { utcTimeNow, showAlert } from '../../../util/timeFunctions'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'


class TableWarns extends Component {
  constructor(props) {
    super(props)

    this.interval = null
    this.state = {
      time: utcTimeNow(),
      tables: props.tables
    }
  }

  render() {
    const { tables, size, staticConfig, classes } = this.props

    const alertOpened = staticConfig.timeToAlertTableOpened
    const alertIsIdle = staticConfig.timeToAlertTableIsIdle
    const alertIsIdleWarning = staticConfig.timeToAlertTableIsIdleWarning
    const filterTables = []

    for (let i = 0; i < tables.length; i++) {
      const hasHoldItems = tables[i].ordersHoldItems != null && tables[i].ordersHoldItems.length > 1
      const noOrderAlert = showAlert(tables[i].startTS, this.state.time, alertOpened)
      const hasIdleAlert = showAlert(tables[i].lastUpdateTS, this.state.time, alertIsIdle)

      if (hasHoldItems || noOrderAlert || hasIdleAlert) {
        filterTables.push(tables[i])
      }
    }

    if (filterTables === []) {
      return <div/>
    }

    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={1} innerClassName={classes.detailsTitle}>
          <I18N id={'$WARNINGS'}/>
        </FlexChild>
        <FlexChild size={size - 1}>
          <ScrollPanel>
            {filterTables.map((currentTable, index) =>
              <div key={index} className={classes.warnsLine} style={{ height: `calc(100% / ${size - 1})` }}>
                <FlexGrid>
                  <FlexChild size={6} innerClassName={classes.centerTable}>
                    <I18N id={'$TABLE'}/>: {currentTable.id}
                  </FlexChild>
                  <FlexChild innerClassName={classes.centerIcon}>
                    {this.renderHoldIcon(currentTable)}
                  </FlexChild>
                  <FlexChild innerClassName={classes.centerIcon}>
                    {this.renderIdleIcon(currentTable, alertIsIdleWarning, alertIsIdle)}
                  </FlexChild>
                  <FlexChild innerClassName={classes.centerIcon}>
                    {this.renderNoOrderIcon(currentTable, alertOpened)}
                  </FlexChild>
                </FlexGrid>
              </div>
            )}
          </ScrollPanel>
        </FlexChild>
      </FlexGrid>
    )
  }

  renderNoOrderIcon(currentTable, alertOpened) {
    if (showAlert(currentTable.startTS, this.state.time, alertOpened)) {
      return <i className={'fa fa-hourglass-end'} aria-hidden="true"/>
    }

    return null
  }

  renderIdleIcon(currentTable, alertIsIdleWarning, alertIsIdle) {
    if (showAlert(currentTable.lastUpdateTS, this.state.time, alertIsIdleWarning)) {
      return <i className={'fas fa-exclamation'} aria-hidden="true"/>
    }

    if (showAlert(currentTable.lastUpdateTS, this.state.time, alertIsIdle)) {
      return <i className={'fas fa-spinner'} aria-hidden="true"/>
    }

    return null
  }

  renderHoldIcon(currentTable) {
    if (currentTable.ordersHoldItems != null && currentTable.ordersHoldItems.length > 1) {
      return <i className={'far fa-hand-paper'} aria-hidden="true"/>
    }

    return null
  }

  componentDidMount() {
    this.interval = setInterval(() => {
      this.setState({ time: utcTimeNow() })
    }, 30000)
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }
}

function mapStateToProps({ staticConfig }) {
  return {
    staticConfig
  }
}

const table = PropTypes.shape({
  id: PropTypes.string,
  startTS: PropTypes.string,
  lastUpdateTS: PropTypes.string
})

TableWarns.propTypes = {
  tables: PropTypes.arrayOf(table),
  size: PropTypes.number,
  staticConfig: StaticConfigPropTypes,
  classes: PropTypes.object
}

export default connect(mapStateToProps)(TableWarns)
