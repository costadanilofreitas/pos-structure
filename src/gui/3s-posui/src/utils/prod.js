import _ from 'lodash'
import { ensureArray } from './order'

const reduceCustom = (custom) =>
  _.reduce(ensureArray(custom || []), (result, value) => {
    const resultRef = result
    const attrs = value['@attributes'] || {}
    const ctx = attrs.context
    if (!ctx) {
      return result
    }
    if (!_.has(resultRef, attrs.context)) {
      resultRef[ctx] = {}
    }
    resultRef[ctx][attrs.key] = attrs.value
    return resultRef
  }, {})

/**
 * Helper function to simplify production's order structure, and ensure that keys
 * that are expected to return an array are consistent.
 *
 * @param order object production order as-is after xmlToJson conversion
 * @return object with simplified structure
 *
 * Return example (simplified)
 * {
 *   attrs: {
 *     business_day: '20180316',
 *     created_at: '2018-03-16T09:48:39.960',
 *     pod_type: 'FC',
 *     pos_id: '1',
 *     sale_type: 'EAT_IN',
 *     state: 'PAID',
 *     total_gross: '15.22',
 *     ...
 *   },
 *   custom: {
 *     'FC-BOX': {
 *       last_state: 'PAID',
 *       ...
 *     },
 *     'PICKLIST-BOX': {
 *       last_state: 'PAID',
 *       prod_state: 'NORMAL',
 *       ...
 *     }
 *   },
 *   items: [
 *     {
 *       attrs: {
 *         default_qty: '0',
 *         description: 'B&C Whopper',
 *         item_code: '1.2000005',
 *         qty: '1',
 *         ...
 *       },
 *       custom: {
 *         Sandwich: {
 *           side: 'Single'
 *         }
 *       }
 *     },
 *     ...
 *   ],
 *   props: {
 *     CUSTOMER_NAME: 'John Doe'
 *   },
 *   stateHistory: [
 *     {
 *       state: 'IN_PROGRESS',
 *       state_id: '1',
 *       timestamp: '2018-03-16T09:48:39.961'
 *     },
 *     {
 *       state: 'TOTALED',
 *       state_id: '3',
 *       timestamp: '2018-03-16T09:48:56.143'
 *     },
 *     ...
 *   ]
 * }
 */
const convertProdOrder = (order) => {
  const ord = order || {}
  const prodOrder = ord.ProductionOrder || {}

  // custom attributes
  const custom = reduceCustom(prodOrder.Custom)

  // convert state history inside custom to JSON
  _.forEach(
    _.keys(custom),
    (key) => {
      try {
        custom[key].state_history = JSON.parse(custom[key].state_history)
      } catch (e) {
        console.error(e)
      }
    }
  )

  const processItems = (items) => {
    const ret = []
    _.forEach(ensureArray(items || []), (item) => {
      const newItem = {
        attrs: item['@attributes'] || {},
        custom: reduceCustom(item.Custom),
        comments: _.map(ensureArray(item.Comment || []),
          (comment) => (comment['@attributes'] || {})
        ),
        items: [],
        tags: [],
        tagHistory: []
      }
      if (item.Item) {
        newItem.items = processItems(item.Item)
      }
      if (item.Tags !== undefined) {
        ensureArray(item.Tags.Tag).forEach(tag => {
          newItem.tags.push(tag['@attributes'].name)
        })
      }
      if (item.TagHistory !== undefined) {
        ensureArray(item.TagHistory.TagEvent).forEach(event => {
          newItem.tagHistory.push({
            tag: event['@attributes'].tag,
            action: event['@attributes'].action,
            timestamp: event['@attributes'].timestamp
          })
        })
      }
      ret.push(newItem)
    })
    return ret
  }

  const orderItems = processItems((prodOrder.Items || {}).Item)

  // order properties (customer name, table number, etc.)
  const props = _.reduce(
    ensureArray((prodOrder.Properties || {}).Property || []),
    (result, value) => {
      const resultRef = result
      const attrs = value['@attributes'] || {}
      resultRef[attrs.key] = attrs.value
      return resultRef
    }, {})

  // order properties (customer name, table number, etc.)
  const stateHistory = _.map(
    ensureArray((prodOrder.StateHistory || {}).StateEvent || []),
    (item) => item['@attributes'] || {}
  )

  return {
    attrs: prodOrder['@attributes'] || {},
    custom,
    items: orderItems,
    props,
    stateHistory
  }
}

export default convertProdOrder
