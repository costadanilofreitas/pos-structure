import React from 'react'
import PropTypes from 'prop-types'

import { ScrollPanel } from '3s-widgets'

import Label from '../../../../component/label'
import SliceServiceButton from './slice-service-button'


function markLineAsSelected(selectedSaleLines, saleLine) {
  if (selectedSaleLines != null) {
    for (let i = 0; i < selectedSaleLines.length; i++) {
      if (selectedSaleLines[i] &&
        selectedSaleLines[i].orderId === saleLine.orderId &&
        selectedSaleLines[i].lineNumber === saleLine.lineNumber &&
        selectedSaleLines[i].itemId === saleLine.itemId &&
        selectedSaleLines[i].partCode === saleLine.partCode) {
        return '#D1D1D1'
      }
    }
  }

  return null
}

export default function SeatItems(props) {
  const { seat, saleLines, selectedSaleLines, onSaleLineSelect, classes, tableId, setSeatScreen } = props
  const propClasses = classes || {}

  const deletedLines = _.filter(saleLines, (saleLine) => saleLine.level === 0 && saleLine.qty === 0)
  const deletedLinesNumbers = _.map(deletedLines, (saleLine) => saleLine.lineNumber)

  const filterSaleLines = []
  for (let i = 0; i < saleLines.length; i++) {
    let found = false
    const saleLine = saleLines[i]
    for (let j = 0; j < deletedLinesNumbers.length; j++) {
      const deletedLine = deletedLinesNumbers[j]
      if (saleLine.lineNumber === deletedLine.lineNumber && saleLine.orderId === deletedLine.orderId) {
        found = true
        break
      }
    }
    if (found === false) {
      filterSaleLines.push(saleLine)
    }
  }

  const orderTotalAmount = filterSaleLines.reduce((amount, saleLine) => {
    return amount + (saleLine.unitPrice * saleLine.multipliedQty)
  }, 0)

  return (
    <div className={propClasses.rootContainer} key={'topContainer'}>
      <div
        style={{ height: (seat === 0 ? '100%' : '85%'), display: 'flex', flexDirection: 'column' }}
        onClick={() => props.onClick(seat)}
      >
        <div className={propClasses.customSalePanelHeaderInfo} key={'titleContainer'}>
          <p className={classes.customSalePanelHeaderColumnLeft}>
            {seat !== 0
              ? <i className="fa fa-user" aria-hidden="true" style={{ margin: '0.5vh' }}/>
              : <i className="fa fa-users" aria-hidden="true" style={{ margin: '0.5vh' }}/>
            }
            {seat !== 0
              ? <Label text={`$SEAT|${seat}`}/>
              : <Label text={'$NO_SEAT'}/>
            }
          </p>
          <p className={classes.customSalePanelHeaderColumnRight}>
            <i className="far fa-money-bill-alt" aria-hidden="true" style={{ margin: '0.5vh' }}/>
            <Label key="orderTotalAmount" text={orderTotalAmount} style="currency"/>
          </p>
        </div>
        <div style={{ flex: '1', position: 'relative', backgroundColor: 'white' }}>
          <ScrollPanel>
            {saleLines.map(saleLine => {
              if (saleLine.level !== 0 || saleLine.qty === 0) {
                return null
              }
              const key = `${saleLine.orderId}${saleLine.lineNumber}${saleLine.itemId}${saleLine.partCode}`
              const background = markLineAsSelected(selectedSaleLines, saleLine)
              const fractionFrom = saleLine.fractionFrom != null ? ` [${parseInt(saleLine.fractionFrom, 10)}]` : ''

              return (
                <p
                  key={`line${key}`}
                  className={classes.seatItem}
                  style={{ backgroundColor: background }}
                  onClick={event => {
                    onSaleLineSelect(saleLine)
                    event.stopPropagation()
                  }}
                >
                  <Label key={key} text={`${saleLine.qty} ${saleLine.productName}${fractionFrom}`}/>
                </p>
              )
            })}
          </ScrollPanel>
        </div>
      </div>
      {seat !== 0 &&
      <div style={{ height: '15%' }}>
        <SliceServiceButton tableId={tableId} saleLines={JSON.stringify(saleLines)} setSeatScreen={setSeatScreen} />
      </div>}
    </div>
  )
}

const SaleLinePropType = PropTypes.shape({
  orderId: PropTypes.number.isRequired,
  lineNumber: PropTypes.number.isRequired,
  itemId: PropTypes.string.isRequired,
  partCode: PropTypes.number.isRequired,
  productName: PropTypes.string.isRequired
})

SeatItems.propTypes = {
  seat: PropTypes.number.isRequired,
  saleLines: PropTypes.arrayOf(SaleLinePropType).isRequired,
  selectedSaleLines: PropTypes.array,
  onSaleLineSelect: PropTypes.func.isRequired,
  onClick: PropTypes.func,
  classes: PropTypes.object,
  tableId: PropTypes.string,
  setSeatScreen: PropTypes.func
}
