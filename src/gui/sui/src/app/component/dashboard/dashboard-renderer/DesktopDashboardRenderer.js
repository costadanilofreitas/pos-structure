import React from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid, Image } from '3s-widgets'

import TablePlan from '../../../component/table-plan'
import DailyGoals from '../../../component/daily-goals'
import { DashboardImage } from '../../../../constants/Images'

export default function DesktopDashboardRenderer({ showInDashboard, tableLists, floorPlan }) {
  if (!showInDashboard || showInDashboard.length === 0) {
    return <div/>
  }

  return (
    <FlexGrid direction={'column'}>
      { showInDashboard.indexOf('FloorPlan') >= 0 && floorPlan.enabled &&
        <FlexChild>
          <TablePlan tables={tableLists} executeTableClick={false}/>
        </FlexChild>
      }
      { showInDashboard.indexOf('DailyGoals') >= 0 &&
        <FlexChild>
          <DailyGoals
            showAmountChart={true}
            showItemsChart={true}
            showOperatorsTable={true}
            showAverageTicketChart={true}
            showSubtitles={true}
            showInAllScreen={true}
            goalsFlexDirection={'column'}
            selectedOperator={''}
          />
        </FlexChild>
      }
      { showInDashboard.indexOf('Image') >= 0 &&
        <FlexChild>
          <Image
            src={['./images/dashboardImageLogo.png', DashboardImage]}
            objectFit={'scale-down'}
            background={'transparent'}
          />
        </FlexChild>
      }
    </FlexGrid>
  )
}

DesktopDashboardRenderer.propTypes = {
  showInDashboard: PropTypes.array,
  tableLists: PropTypes.object,
  floorPlan: PropTypes.shape({
    enabled: PropTypes.bool
  })
}
