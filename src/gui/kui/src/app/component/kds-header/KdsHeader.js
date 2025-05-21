import React, { Component } from 'react'
import { FlexChild, FlexGrid } from '3s-widgets'
import { ensureArray } from '3s-posui/utils'
import isEqual from 'lodash/isEqual'
import PropTypes from 'prop-types'
import { KdsHeaderContainer } from './StyledKdsHeader'
import StatisticsRender from './StatisticsRender'


export default class KdsHeader extends Component {
  shouldComponentUpdate(nextProps) {
    return (!isEqual(this.props.statistics, nextProps.statistics))
  }

  render() {
    const { statistics, views } = this.props
    const arrayViews = ensureArray(views)
    const currentView = arrayViews.find(x => x.selected === true)

    if (currentView.statistics.length === 0) {
      return null
    }

    return (
      <FlexChild size={1.5}>
        <KdsHeaderContainer className={'test_KdsHeader_HEADER'}>
          <FlexGrid direction={'row'}>
            <FlexChild size={3}>
              <StatisticsRender statisticsValues={statistics} viewStatistics={currentView.statistics}/>
            </FlexChild>
          </FlexGrid>
        </KdsHeaderContainer>
      </FlexChild>
    )
  }
}

KdsHeader.propTypes = {
  statistics: PropTypes.object,
  views: PropTypes.array
}
