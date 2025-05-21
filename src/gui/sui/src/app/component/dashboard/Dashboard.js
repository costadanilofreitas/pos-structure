import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import DesktopDashboardRenderer from './dashboard-renderer'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'

class Dashboard extends Component {
  render() {
    const { staticConfig, tableLists, floorPlan } = this.props
    return (
      <DesktopDashboardRenderer
        showInDashboard={staticConfig.showInDashboard}
        tableLists={tableLists}
        floorPlan={floorPlan}
      />
    )
  }
}

function mapStateToProps({ staticConfig }) {
  return {
    staticConfig
  }
}

Dashboard.propTypes = {
  staticConfig: StaticConfigPropTypes,
  tableLists: PropTypes.object,
  floorPlan: PropTypes.shape({
    enabled: PropTypes.bool
  })
}

export default connect(mapStateToProps)(Dashboard)
