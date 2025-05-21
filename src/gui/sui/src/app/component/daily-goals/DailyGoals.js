import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import DailyGoalsRender from './daily-goals-renderer'
import propTypes from '../custom-sale-panel/sale-panel/summary/propTypes'


export default class DailyGoals extends Component {
  constructor(props) {
    super(props)

    this.state = {
      selectedOperator: this.props.selectedOperator
    }

    this.handleOnOperatorClick = this.handleOnOperatorClick.bind(this)
  }

  render() {
    const storeGoals = this.props.dailyGoals != null ? this.props.dailyGoals.store_goals : undefined
    const operatorGoals = this.props.dailyGoals != null ? this.props.dailyGoals.operator_goals : []

    if (storeGoals == null && (operatorGoals == null || operatorGoals.length === 0)) {
      return (
        <div style={{ display: 'flex', height: '100%', justifyContent: 'center', alignItems: 'center' }}>
          <I18N id="$NO_GOALS_AVAILABLE"/>
        </div>
      )
    }

    const selectedOperator = this.state.selectedOperator
    operatorGoals.sort((a, b) => (parseInt(a.id, 10) > parseInt(b.id, 10)) ? 1 : -1)

    const itemGoals = storeGoals != null ? storeGoals.item_goals : []
    const storeGoalsData = storeGoals != null
      ? this.populateSalesGoals(selectedOperator, storeGoals, operatorGoals)
      : []
    const itemGoalsData = this.populateItemsGoals(selectedOperator, itemGoals, operatorGoals)
    const storeAmount = operatorGoals.length > 0 ? operatorGoals.reduce((a, b) => a + (b.amount_sold || 0), 0) : 0
    let storeQuantity = 0
    let storeTickets = 0

    if (operatorGoals.length > 0) {
      for (let i = 0; i < operatorGoals.length; i++) {
        for (let j = 0; j < operatorGoals[i].item_goals.length; j++) {
          storeQuantity += operatorGoals[i].item_goals[j].quantity_sold
        }
        storeTickets += operatorGoals[i].tickets
      }
    }

    const averageTicketGoalData = this.populateAverageTicketGoals(
      selectedOperator,
      storeGoals,
      storeAmount,
      storeTickets,
      operatorGoals)

    return (
      <DailyGoalsRender
        {...this.props}
        selectedOperator={this.state.selectedOperator}
        itemGoals={itemGoalsData}
        storeGoals={storeGoalsData}
        operatorGoals={operatorGoals}
        storeAmount={storeAmount}
        storeQuantity={storeQuantity}
        storeTickets={storeTickets}
        averageTicketGoalData={averageTicketGoalData}
        onOperatorClick={this.handleOnOperatorClick}
      />
    )
  }

  populateSalesGoals(selectedOperator, storeGoals, operatorGoals) {
    const storeGoalsData = []
    if (selectedOperator === '') {
      let remainingPercentage = (((storeGoals.amount_goal - storeGoals.sold_quantity) / storeGoals.amount_goal) * 100)
      remainingPercentage = remainingPercentage.toFixed(2)
      let reachedPercentage = ((storeGoals.sold_quantity / storeGoals.amount_goal) * 100).toFixed(2)

      if (parseFloat(remainingPercentage) < 0) {
        reachedPercentage = '100.00'
        remainingPercentage = '0.00'
      }

      storeGoalsData.push([`${remainingPercentage}%`, (storeGoals.amount_goal - storeGoals.sold_quantity),
        this.props.theme.dailyGoalsColor])
      storeGoalsData.push([`${reachedPercentage}%`, storeGoals.sold_quantity, this.props.theme.dailyGoalsColorReached])
    } else {
      const operatorGoal = operatorGoals.filter(function (el) {
        return el.id === selectedOperator
      })[0]

      if (operatorGoal == null) {
        return storeGoalsData
      }

      let remainingValue = operatorGoal.amount_goal - operatorGoal.amount_sold
      remainingValue = remainingValue < 0 ? 0 : remainingValue

      const remainingPercentage = ((remainingValue / operatorGoal.amount_goal) * 100).toFixed(2)
      let reachedPercentage = ((operatorGoal.amount_sold / operatorGoal.amount_goal) * 100).toFixed(2)

      if (parseFloat(reachedPercentage) > 100) {
        reachedPercentage = '100.00'
      }

      storeGoalsData.push([`${remainingPercentage}%`, remainingValue, this.props.theme.dailyGoalsColor])
      storeGoalsData.push([`${reachedPercentage}%`, operatorGoal.amount_sold, this.props.theme.dailyGoalsColorReached])
    }
    return storeGoalsData
  }

  populateItemsGoals(selectedOperator, itemGoals, operatorGoals) {
    const itemGoalsGoal = []
    const itemGoalsData = []

    if (selectedOperator === '') {
      if (itemGoals.length === 0) {
        return []
      }

      const newItemGoals = this.orderArrayByProperty(itemGoals).slice(0, 3)
      for (let i = 0; i < newItemGoals.length; i++) {
        const name = newItemGoals[i].name
        const soldQuantity = newItemGoals[i].quantity_sold
        const quantityGoal = newItemGoals[i].quantity_goal
        itemGoalsGoal.push({ x: name, y: quantityGoal, style: { fontSize: '1.5vmin' } })
        itemGoalsData.push({ x: name, y: soldQuantity, style: { fontSize: '1.5vmin' } })
      }

      return [itemGoalsGoal, itemGoalsData]
    }

    for (let i = 0; i < operatorGoals.length; i++) {
      if (operatorGoals[i].id === selectedOperator) {
        operatorGoals[i].item_goals = this.orderArrayByProperty(operatorGoals[i].item_goals).slice(0, 3)
        for (let j = 0; j < operatorGoals[i].item_goals.length; j++) {
          const name = operatorGoals[i].item_goals[j].name
          const soldQuantity = operatorGoals[i].item_goals[j].quantity_sold
          const quantityGoal = operatorGoals[i].item_goals[j].quantity_operator_goal

          if (itemGoalsData.filter((el) => el[0] === name).length > 0) {
            for (let k = 0; k < itemGoalsData.length; k++) {
              if (itemGoalsData[k][0] === name) {
                itemGoalsData[k][2] += (soldQuantity / quantityGoal) * 100
              }
            }
          } else {
            itemGoalsGoal.push({ x: name, y: quantityGoal })
            itemGoalsData.push({ x: name, y: soldQuantity })
          }
        }
      }
    }

    return [itemGoalsGoal, itemGoalsData]
  }

  orderArrayByProperty(items) {
    return items.sort((a, b) => {
      if (a.quantity_goal < b.quantity_goal) {
        return 1
      }
      if (b.quantity_goal < a.quantity_goal) {
        return -1
      }
      return 0
    })
  }

  populateAverageTicketGoals(selectedOperator, storeGoals, storeAmount, storeTickets, operatorGoals) {
    const averageTicketGoalsData = []
    if (selectedOperator === '') {
      const averageSaleGoal = storeTickets === 0 ? 0 : storeAmount / storeTickets
      averageTicketGoalsData.push([{ y: 1, x: 0 }, { y: 2, x: storeGoals.average_sale_goal }])
      averageTicketGoalsData.push([{ y: 1, x: averageSaleGoal }, { y: 2, x: 0 }])
    } else {
      const operatorGoal = operatorGoals.filter(function (el) {
        return el.id === selectedOperator
      })[0]

      if (operatorGoal == null) {
        return averageTicketGoalsData
      }

      const averageSaleGoal = operatorGoal.tickets === 0 ? 0 : operatorGoal.amount_sold / operatorGoal.tickets
      averageTicketGoalsData.push([{ y: 1, x: 0 }, { y: 2, x: operatorGoal.average_ticket }])
      averageTicketGoalsData.push([{ y: 1, x: averageSaleGoal }, { y: 2, x: 0 }])
    }
    return averageTicketGoalsData
  }

  handleOnOperatorClick(selectedOperator) {
    this.setState({ selectedOperator })
  }
}

DailyGoals.propTypes = {
  dailyGoals: PropTypes.object,
  selectedOperator: PropTypes.string.isRequired,
  showAmountChart: PropTypes.bool.isRequired,
  showItemsChart: PropTypes.bool.isRequired,
  showOperatorsTable: PropTypes.bool.isRequired,
  showAverageTicketChart: PropTypes.bool.isRequired,
  showInAllScreen: PropTypes.bool,
  showSubtitles: PropTypes.bool,
  goalsFlexDirection: PropTypes.string,
  theme: propTypes.object
}
