import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import Label from '../../../../../component/label/Label'
import ActionButton from '../../../../../component/action-button/JssActionButton'


export default class TableOrderHeader extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { order, currentTime, showExpand } = this.props
    const classes = this.props.classes || {}
    const orderHasHoldItem = order.saleLines.some(saleLine => !!saleLine.hold && saleLine.qty > 0)
    const expandIcon = this.props.isExpanded ? 'fa-angle-down' : 'fa-angle-right'
    const angleButton = this.props.isExpanded ? ' test_TableOrderHeader_DOWN' : ' test_TableOrderHeader_RIGHT'
    return (
      <div className={classes.customSalePanelHeader}>
        <FlexGrid direction={'row'}>
          {showExpand && (
            <FlexChild size={15}>
              <ActionButton
                className={`${classes.button} test_TableOrderHeader_OPTIONS`}
                onClick={() => this.props.onOrderChange(order)}
                blockOnActionRunning={true}
              >
                <i className="fa fa-cog fa-3x" aria-hidden="true" style={{ margin: '0.5vh' }}/><br/>
              </ActionButton>
            </FlexChild>
          )}
          <FlexChild size={70}>
            <FlexGrid direction={'column'} className={showExpand ? classes.headerInnerInfo : ''}>
              <FlexChild>
                <FlexGrid>
                  <FlexChild size={3} innerClassName={classes.displayCenteredLeftItem}>
                    <p className={classes.customSalePanelHeaderTitleColumnLeft}>
                      <i className="fas fa-pen-square" aria-hidden="true" style={{ margin: '0.5vh' }}/>
                      <I18N id={`$ORDER_NUMBER|${order.orderId}`}/>
                      {orderHasHoldItem && (
                        <i className={`far fa-hand-paper ${classes.faHandIcon}`} aria-hidden="true"/>
                      )}
                    </p>
                  </FlexChild>
                  <FlexChild size={1} innerClassName={classes.displayCenteredRightItem}>
                    <p className={classes.customSalePanelHeaderTitleColumnRight}>
                      [<I18N id={`$${order.saleTypeDescr}`}/>]
                    </p>
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
              <FlexChild>
                <FlexGrid>
                  <FlexChild size={1} innerClassName={classes.displayCenteredLeftItem}>
                    <p className={classes.customSalePanelHeaderColumnLeft}>
                      <i className="far fa-clock" aria-hidden="true" style={{ margin: '0.5vh' }}/>
                      <Label
                        key={'orderTime'}
                        text={currentTime.getTime() - order.createdAtGMT.getTime()}
                        style="datetimeMillisecondsSpan"
                      />
                    </p>
                  </FlexChild>
                  <FlexChild size={1} innerClassName={classes.displayCenteredRightItem}>
                    <p className={classes.customSalePanelHeaderColumnRight}>
                      <i className="fas fa-coins" aria-hidden="true" style={{ margin: '0.5vh' }}/>
                      <Label key="orderTotalAmount" text={order.totalGross} style="currency"/>
                    </p>
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
            </FlexGrid>
          </FlexChild>
          {showExpand && (
            <FlexChild size={15}>
              <ActionButton
                className={classes.button + angleButton}
                onClick={this.props.onExpand}
                blockOnActionRunning={true}
              >
                <i className={`${classes.expandIcon} fas ${expandIcon} fa-4x`} aria-hidden="true"/>
              </ActionButton>
            </FlexChild>
          )}
        </FlexGrid>
      </div>
    )
  }
}

TableOrderHeader.propTypes = {
  order: PropTypes.object,
  tableStatus: PropTypes.number.isRequired,
  currentTime: PropTypes.object,
  showExpand: PropTypes.bool,
  onExpand: PropTypes.func,
  isExpanded: PropTypes.bool,
  onOrderChange: PropTypes.func,

  classes: PropTypes.object
}
