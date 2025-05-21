import React, { Component } from 'react'
import PropTypes from 'prop-types'
import {
  RadialChart,
  XYPlot,
  XAxis,
  YAxis,
  VerticalGridLines,
  HorizontalGridLines,
  VerticalBarSeries,
  HorizontalBarSeries
} from 'react-vis'
import AutoSizer from 'react-virtualized/dist/commonjs/AutoSizer'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'

import Label from '../../../../component/label/Label'


export default class DailyGoalsRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const {
      classes,
      itemGoals,
      showAmountChart,
      showItemsChart,
      showOperatorsTable,
      showAverageTicketChart,
      showInAllScreen,
      goalsFlexDirection
    } = this.props

    const amountChartData = this.initializeAmountChartData()
    const itemsChartData = itemGoals
    const showFirstChart = showAmountChart || showItemsChart
    const showSecondChart = showOperatorsTable || showAverageTicketChart

    return (
      <div className={classes.dailyGoalsMainContainer}>
        <FlexGrid direction={'row'}>
          {showFirstChart &&
          <FlexChild outerClassName={!(showAmountChart && showItemsChart) && !showInAllScreen ?
            classes.oneChart : ''}
          >
            <FlexGrid direction={goalsFlexDirection}>
              <FlexChild>
                {showAmountChart && this.renderAmountChart(amountChartData)}
              </FlexChild>
              {showItemsChart && itemsChartData.length > 1 &&
              this.renderItemsChart(itemsChartData)
              }
            </FlexGrid>
          </FlexChild>
          }
          {showSecondChart &&
          <FlexChild outerClassName={!(showOperatorsTable && showAverageTicketChart) && !showInAllScreen ?
            classes.oneChart : ''}
          >
            <FlexGrid direction={goalsFlexDirection}>
              {showOperatorsTable &&
              this.renderOperatorsTable(itemsChartData)
              }
              {showAverageTicketChart && itemsChartData.length > 1 &&
              this.renderAverageTicketChart()
              }
            </FlexGrid>
          </FlexChild>
          }
        </FlexGrid>
      </div>
    )
  }

  initializeAmountChartData() {
    const { storeGoals } = this.props
    const pieChartData = []
    storeGoals.map((value) => pieChartData.push(({ angle: value[1], color: value[2], name: value[0] })))
    return pieChartData
  }

  renderAmountChart(pieChartData) {
    const { classes, showSubtitles } = this.props
    return (
      <FlexGrid direction={'column'}>
        {showSubtitles &&
        <FlexChild>
          <p className={classes.chartTitle}><I18N id={'$DAILY_GOALS_BY_AMOUNT'}/></p>
        </FlexChild>
        }
        <FlexChild size={10} innerClassName={classes.centerItems}>
          <div className={'container'}>
            <AutoSizer>
              {({ width, height }) => (
                <RadialChart
                  colorType={'literal'}
                  colorDomain={[0, 100]}
                  colorRange={[0, 10]}
                  margin={{ top: 0 }}
                  getLabel={d => d.name}
                  data={pieChartData}
                  labelsRadiusMultiplier={0.9}
                  labelsStyle={{ fontSize: 16, fill: 'white' }}
                  showLabels
                  style={{ stroke: '#fff', strokeWidth: 2 }}
                  width={width}
                  height={height}
                />
              )}
            </AutoSizer>
          </div>
        </FlexChild>
        {showSubtitles &&
        <FlexChild innerClassName={classes.centerItems}>
          <p className={classes.chartInfo}>
            <span className={classes.chartInfoSquareReached}/><I18N id={'$REMAINING'}/>
          </p>
          <p className={classes.chartInfo}>
            <span className={classes.chartInfoSquareGoal}/><I18N id={'$REACHED'}/>
          </p>
        </FlexChild>}
      </FlexGrid>
    )
  }

  renderItemsChart(itemsChartData) {
    const { classes, showSubtitles, theme } = this.props
    return (
      <FlexChild innerClassName={classes.centerItems}>
        <FlexGrid direction={'column'}>
          {showSubtitles &&
          <FlexChild>
            <p className={classes.chartTitle}><I18N id={'$DAILY_GOALS_STORE_BY_CATEGORY'}/></p>
          </FlexChild>
          }
          <FlexChild size={10} innerClassName={classes.centerItems}>
            <div className={'container'}>
              <AutoSizer>
                {({ width, height }) => (
                  <XYPlot xType="ordinal" width={width} height={height}>
                    <VerticalGridLines/>
                    <HorizontalGridLines style={{ stroke: '#000000', strokeWidth: 1 }}/>
                    <XAxis/>
                    <YAxis/>
                    <VerticalBarSeries
                      data={itemsChartData[0]}
                      style={{ fill: theme.dailyGoalsColor, stroke: theme.dailyGoalsColor }}
                    />
                    <VerticalBarSeries
                      data={itemsChartData[1]}
                      style={{ fill: theme.dailyGoalsColorReached, stroke: theme.dailyGoalsColorReached }}
                    />
                  </XYPlot>
                )}
              </AutoSizer>
            </div>
          </FlexChild>
          {showSubtitles &&
          <FlexChild innerClassName={classes.centerItems}>
            <p className={classes.chartInfo}>
              <span className={classes.chartInfoSquareReached}/><I18N id={'$GOAL'}/>
            </p>
            <p className={classes.chartInfo}>
              <span className={classes.chartInfoSquareGoal}/><I18N id={'$REACHED'}/>
            </p>
          </FlexChild>
          }
        </FlexGrid>
      </FlexChild>
    )
  }

  renderOperatorsTable(itemsChartData) {
    const {
      classes,
      selectedOperator,
      operatorGoals,
      storeAmount,
      storeQuantity,
      storeTickets
    } = this.props

    return (
      <FlexChild>
        <ScrollPanel style={{ height: '100%', position: 'absolute', fontSize: '2vmin' }}>
          <div className={classes.flexTableTitle}>
            <div className={classes.flexRow}><I18N id={'$OPERATOR'}/></div>
            <div className={classes.flexRow}>$</div>
            {itemsChartData.length > 1 && <div className={classes.flexRow}>#</div>}
            <div className={classes.flexRow}>TM</div>
          </div>
          <div
            className={selectedOperator === '' ? classes.flexTableSelected : classes.flexTable}
            onClick={() => this.props.onOperatorClick('')}
          >
            <div className={classes.flexRow}><I18N id={'$STORE'}/></div>
            <div className={classes.flexRow}>
              <Label text={storeAmount} style="currency"/>
            </div>
            {itemsChartData.length > 1 &&
            <div className={classes.flexRow}>
              {storeQuantity}
            </div>
            }
            <div className={classes.flexRow}>
              <Label text={storeTickets === 0 ? 0 : storeAmount / storeTickets} style="currency"/>
            </div>
          </div>
          {operatorGoals.length > 0 && operatorGoals.map((value) => (
            <div
              key={`operator_${value.id}`}
              className={selectedOperator === value.id ? classes.flexTableSelected : classes.flexTable}
              onClick={() => this.props.onOperatorClick(value.id)}
            >
              <div className={classes.flexRow}>
                {value.id}
              </div>
              <div className={classes.flexRow}>
                <Label text={value.amount_sold} style="currency"/>
              </div>
              {itemsChartData.length > 1 &&
              <div className={classes.flexRow}>
                {value.item_goals.reduce((a, b) => a + (b.quantity_sold || 0), 0)}
              </div>
              }
              <div className={classes.flexRow}>
                <Label text={value.tickets === 0 ? 0 : value.amount_sold / value.tickets} style="currency"/>
              </div>
            </div>
          ))
          }
        </ScrollPanel>
      </FlexChild>
    )
  }

  renderAverageTicketChart() {
    const {
      classes,
      averageTicketGoalData,
      showSubtitles,
      theme
    } = this.props

    return (
      <FlexChild innerClassName={classes.centerItems}>
        <FlexGrid direction={'column'}>
          {showSubtitles &&
          <FlexChild>
            <p className={classes.chartTitle}><I18N id={'$DAILY_GOALS_STORE_BY_AVERAGE_TICKET'}/></p>
          </FlexChild>
          }
          <FlexChild size={10} innerClassName={classes.centerItems}>
            <div className={'container'}>
              <AutoSizer>
                {({ width, height }) => (
                  <XYPlot
                    width={width}
                    height={height}
                    stackBy="x"
                  >
                    <VerticalGridLines style={{ stroke: '#000000', strokeWidth: 1 }}/>
                    <XAxis/>
                    <HorizontalBarSeries
                      data={averageTicketGoalData[0]}
                      style={{ fill: theme.dailyGoalsColor, stroke: theme.dailyGoalsColor }}
                    />
                    <HorizontalBarSeries
                      data={averageTicketGoalData[1]}
                      style={{ fill: theme.dailyGoalsColorReached, stroke: theme.dailyGoalsColorReached }}
                    />
                  </XYPlot>
                )}
              </AutoSizer>
            </div>
          </FlexChild>
          {showSubtitles &&
          <FlexChild innerClassName={classes.centerItems}>
            <p className={classes.chartInfo}>
              <span className={classes.chartInfoSquareReached}/><I18N id={'$GOAL'}/>
            </p>
            <p className={classes.chartInfo}>
              <span className={classes.chartInfoSquareGoal}/><I18N id={'$REACHED'}/>
            </p>
          </FlexChild>
          }
        </FlexGrid>
      </FlexChild>
    )
  }
}

DailyGoalsRenderer.propTypes = {
  classes: PropTypes.object,
  selectedOperator: PropTypes.string.isRequired,
  itemGoals: PropTypes.array,
  storeGoals: PropTypes.array,
  operatorGoals: PropTypes.array,
  storeAmount: PropTypes.number,
  storeQuantity: PropTypes.number,
  storeTickets: PropTypes.number,
  averageTicketGoalData: PropTypes.array,
  showAmountChart: PropTypes.bool.isRequired,
  showItemsChart: PropTypes.bool.isRequired,
  showOperatorsTable: PropTypes.bool.isRequired,
  showAverageTicketChart: PropTypes.bool.isRequired,
  showInAllScreen: PropTypes.bool,
  showSubtitles: PropTypes.bool,
  goalsFlexDirection: PropTypes.string.isRequired,
  onOperatorClick: PropTypes.func,
  theme: PropTypes.object
}
