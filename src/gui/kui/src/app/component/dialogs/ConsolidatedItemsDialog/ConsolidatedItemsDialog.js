import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'
import { FlexChild } from '3s-widgets'
import lodash from 'lodash'

import {
  ConsolidatedItemsDialogBox,
  ConsolidatedItemsDialogClose,
  ConsolidatedItemsDialogContainer,
  ConsolidatedItemsDialogTitle,
  ConsolidatedItemsList,
  ConsolidatedItemsListContainer
} from './StyledConsolidatedItemsDialog'


class ConsolidatedItemsDialog extends Component {
  buildItemKey(item, key = '', isParentProduct = false) {
    let newKey = key + item.attrs.part_code.toString()
    if (isParentProduct) {
      newKey += item.attrs.qty.toString()
    }
    item.items.forEach(son => {
      const isNewParentProduct = item.attrs.item_type.toUpperCase() === 'PRODUCT'
      newKey += this.buildItemKey(son, newKey, isNewParentProduct)
    })
    return newKey
  }

  formatCanAdds(items) {
    const formattedItems = []
    items.forEach(item => {
      if (parseInt(item.attrs.qty, 10) > 0) {
        formattedItems.push(
          {
            quantity: item.attrs.qty,
            description: item.attrs.description
          }
        )
      } else {
        formattedItems.push(
          {
            quantity: '$WITHOUT',
            description: item.attrs.description
          }
        )
      }
    })
    return formattedItems
  }

  collapseItems(allItems) {
    const collapsedItems = {}
    const orderList = []
    let key = ''
    allItems.forEach(order => {
      if (!orderList.includes(order.attrs.order_id)) {
        orderList.push(order.attrs.order_id)
        order.items.forEach(item => {
          if (item.tags.includes('dont-need-cook')) {
            return
          }

          key = this.buildItemKey(item)
          if (!(key in collapsedItems)) {
            collapsedItems[key] = {}
            collapsedItems[key].id = key
            collapsedItems[key].quantity = parseInt(item.attrs.qty, 10)
            collapsedItems[key].description = item.attrs.description
            collapsedItems[key].canAdds = this.formatCanAdds(item.items)
          } else {
            collapsedItems[key].quantity += parseInt(item.attrs.qty, 10)
          }
        })
      }
    })
    return collapsedItems
  }

  renderCanAdds(canAdds) {
    return canAdds.map((canAdd) => (
      <li key={`${canAdd.quantity}_${canAdd.description}`}>
        <I18N id={canAdd.quantity}/> {canAdd.description}
      </li>
    ))
  }

  renderConsolidatedItems(collapsedItems) {
    return Object.values(collapsedItems).map((currentItem) => (
      <li key={currentItem.id}>
        {currentItem.quantity} {currentItem.description}
        <ul>
          {this.renderCanAdds(currentItem.canAdds)}
        </ul>
      </li>
    ))
  }

  render() {
    const allItems = lodash.cloneDeep(this.props.items)
    const collapsedItems = this.collapseItems(allItems)

    return (
      <ConsolidatedItemsDialogContainer>
        <ConsolidatedItemsDialogBox>
          <FlexChild size={1}>
            <ConsolidatedItemsDialogTitle>
              <I18N id={'$PRODUCTS_RESUME'} />
            </ConsolidatedItemsDialogTitle>
          </FlexChild>
          <FlexChild size={8}>
            <ConsolidatedItemsListContainer>
              <ConsolidatedItemsList className={'test_ConsolidatedItems_CONTAINER'}>
                {this.renderConsolidatedItems(collapsedItems)}
              </ConsolidatedItemsList>
            </ConsolidatedItemsListContainer>
          </FlexChild>
          <FlexChild size={1}>
            <ConsolidatedItemsDialogClose
              className={'test_ConsolidatedItems_CLOSE'}
              onClick={() => this.props.handleClose()}>
              <I18N id={'$CLOSE'} />
            </ConsolidatedItemsDialogClose>
          </FlexChild>
        </ConsolidatedItemsDialogBox>
      </ConsolidatedItemsDialogContainer>
    )
  }
}

ConsolidatedItemsDialog.propTypes = {
  items: PropTypes.array,
  handleClose: PropTypes.func
}


export default ConsolidatedItemsDialog
