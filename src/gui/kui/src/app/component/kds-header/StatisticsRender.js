import React, { PureComponent } from 'react'
import axios from 'axios'
import PropTypes from 'prop-types'
import { FlexChild, FlexGrid } from '3s-widgets'
import { I18N } from '3s-posui/core'
import { Goal, KdsStatisticContainer, Statistic, StatisticsValue } from './StyledKdsHeader'

export default class StatisticsRender extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      goalConfig: {}
    }
  }

  statisticTimeToSecond(hours, minutes, seconds) {
    return ((parseInt(hours, 10)) * 3600) + ((parseInt(minutes, 10)) * 60) + parseInt(seconds, 10)
  }

  checkStatisticOverGoal(format, value, goalValue) {
    if (value == null || goalValue == null || format === '') {
      return false
    }

    if (format.startsWith('TIME')) {
      const goalTime = this.getTimeInSeconds(goalValue)
      const valueTime = this.getTimeInSeconds(value)

      return format.endsWith('OVER') ? valueTime > goalTime : valueTime < goalTime
    }

    const percentageGoal = parseFloat(goalValue.replace(/%/g, ''))
    const percentageValue = parseFloat(value)
    return format.endsWith('OVER') ? percentageValue > percentageGoal : percentageValue < percentageGoal
  }

  getTimeInSeconds(timeString) {
    let timeSplit = timeString.split(':').reverse()
    timeSplit = timeSplit.concat(['0', '0'])
    return this.statisticTimeToSecond(timeSplit[2], timeSplit[1], timeSplit[0])
  }

  statisticsRenderer() {
    const { statisticsValues, viewStatistics } = this.props
    const { goalConfig } = this.state

    return Object.values(viewStatistics).map((statistic) => {
      const isPercentage = statistic.format.startsWith('PERCENTAGE')
      const value = statisticsValues[statistic.name] || '-'
      const isAlert = this.checkStatisticOverGoal(statistic.format, value, goalConfig[statistic.name])
      const goal = goalConfig[statistic.name]
      const statisticClassName = `test_StatisticsRender_${statistic.name.replace('$', '').replace('_', '-')}`
      const statisticName = statistic.name
      return (
        <FlexChild size={1} key={`${statistic.name}-${statistic.format}`}>
          <FlexGrid direction={'column'}>
            <FlexChild size={1}>
              <Statistic isAlert={isAlert} className={statisticClassName}>
                <I18N id={statisticName}/>:
                &nbsp;
                <StatisticsValue isAlert={isAlert}>{value}{isPercentage ? '%' : ''}</StatisticsValue>
              </Statistic>
            </FlexChild>
            {(goal != null) &&
            <FlexChild size={1}>
              <Goal>
                <I18N id={'$GOAL'}/>:
                &nbsp;{goal}
              </Goal>
            </FlexChild>}
          </FlexGrid>
        </FlexChild>
      )
    })
  }

  render() {
    return (
      <KdsStatisticContainer>
        <FlexGrid direction={'row'}>
          {this.statisticsRenderer()}
        </FlexGrid>
      </KdsStatisticContainer>
    )
  }

  componentDidMount() {
    axios.get(`/kui/static/goalTimeConfig.json?timestamp=${new Date().getTime()}`)
      .then(response => (this.setState({ goalConfig: response.data })))
      .catch(e => console.error(e))
  }
}

StatisticsRender.propTypes = {
  statisticsValues: PropTypes.object,
  viewStatistics: PropTypes.array
}

StatisticsRender.defaultProps = {
  statisticsValues: [],
  viewStatistics: []
}

