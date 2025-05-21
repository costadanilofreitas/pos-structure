import _ from 'lodash'
import React from 'react'
import Enzyme, { render, shallow, mount } from 'enzyme'
import Adapter from 'enzyme-adapter-react-15.4'

Enzyme.configure({ adapter: new Adapter() })

global.shallow = shallow
global.render = render
global.mount = mount

const mockMath = Object.create(global.Math)
mockMath.random = () => 0.5
global.Math = mockMath

const mockDate = new Date('2017-01-01T00:00:00')
mockDate.setUTCHours(0, 0, 0, 0)
global.origDate = global.Date
global.Date = class extends Date {
  constructor() {
    super()
    return mockDate
  }
}

document.getElementsByTagName('head')[0].appendChild(document.createComment('posui-css-insertion-point'))

function renderComponent(ComponentClass, props = {}) {
  return render(
    <ComponentClass {...props} />
  )
}

function shallowComponent(ComponentClass, props = {}) {
  return shallow(
    <ComponentClass {...props} />
  )
}

function mountComponent(ComponentClass, props = {}, options = {}) {
  return mount(
    <ComponentClass {...props} />,
    options
  )
}

export const createProdOrder = (orderId = 1, numLines = 1, posId = 1, addComments = false) => {
  const items = []
  _.forEach(_.range(numLines), line => {
    const num = line + 1
    const comments = []
    if (addComments) {
      comments.push({
        id: num,
        comment: `Comment ${num}`
      })
    }
    items.push({
      attrs: {
        default_qty: '0',
        description: `Item ${num}`,
        item_code: `1.${num}`,
        item_id: `${num}`,
        item_type: 'PRODUCT',
        json_tags: '',
        level: '0.0',
        line_number: `${num}`,
        max_qty: '0',
        min_qty: '0',
        multiplied_qty: '1',
        only: 'false',
        part_code: `${num}`,
        product_priority: '100',
        qty: '1',
        qty_added: '0',
        qty_modified: '0',
        qty_voided: '0'
      },
      custom: {
        Sandwich: {
          side: 'Single'
        }
      },
      comments
    })
  })
  return {
    attrs: {
      box: 'Sandwich',
      business_day: '20180320',
      buzz_flag: 'False',
      cloned: 'True',
      created_at: '2018-03-20T11:07:53.315',
      created_at_gmt: '2018-03-20T14:07:53.315',
      display_time: '2018-03-20T11:07:57.693',
      image_md5: '',
      major: `${orderId}`,
      minor: '0',
      multiorder_flag: 'False',
      operator_id: '0',
      operator_name: '',
      operator_level: '0',
      order_id: `${orderId}`,
      order_subtype: '',
      order_type: 'SALE',
      originator: `POS000${posId}`,
      originator_number: '0',
      period: '20180320',
      pod_type: 'FC',
      pos_id: `${posId}`,
      product_priority: '0',
      purged: 'True',
      recalled: 'False',
      sale_type: 'EAT_IN',
      session_id: `pos=${posId},user=1,count=1,period=20180320`,
      show_timer: 'True',
      state: 'PAID',
      state_id: '5',
      tagged_lines: '',
      tax_total: '2.18',
      total_gross: '26.35'
    },
    custom: {
      Sandwich: {
        state_history: [
          {
            state: 'IN_PROGRESS',
            state_id: '1',
            timestamp: '2018-03-20T15:45:44.701'
          },
          {
            state: 'TOTALED',
            state_id: '3',
            timestamp: '2018-03-20T15:45:52.084'
          },
          {
            state: 'PAID',
            state_id: '5',
            timestamp: '2018-03-20T15:45:53.309'
          },
          {
            prod_state: 'NORMAL',
            timestamp: '2018-03-20T18:45:44.715650'
          }
        ]
      }
    },
    items,
    props: {},
    stateHistory: [
      {
        state: 'IN_PROGRESS',
        state_id: '1',
        timestamp: '2018-03-20T15:45:44.701'
      },
      {
        state: 'TOTALED',
        state_id: '3',
        timestamp: '2018-03-20T15:45:52.084'
      },
      {
        state: 'PAID',
        state_id: '5',
        timestamp: '2018-03-20T15:45:53.309'
      },
      {
        prod_state: 'NORMAL',
        timestamp: '2018-03-20T18:45:44.715650'
      }
    ]
  }
}

export { renderComponent, shallowComponent, mountComponent }
