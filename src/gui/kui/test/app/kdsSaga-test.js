import { createProdOrder } from '../helper'
import { getFlatLines } from '../../src/app/kdsSaga'

let mockDate = global.Date

const sortLines = (lines) => {
  lines.sort((lineA, lineB) => {
    const prodSeqA = lineA.attrs.prod_sequence
    const prodSeqB = lineB.attrs.prod_sequence
    if (prodSeqA !== '' && prodSeqB !== '') {
      if (prodSeqA > prodSeqB) {
        return -1
      }
      if (prodSeqA < prodSeqB) {
        return 1
      }

      return 0
    }
  })
  return lines
}

beforeAll(() => {
  global.Date = global.origDate
})

afterAll(() => {
  global.Date = mockDate
})

describe('sortLines testing', () => {
  const order1 = createProdOrder(1, 10)
  const order2 = createProdOrder(2, 10)
  // make order 2 timestamp previous to order 1 to test sorting
  order2.custom.Sandwich.state_history[0].timestamp = '2018-03-20T14:30:00.000'
  const lines = [...getFlatLines(order1).normal, ...getFlatLines(order2).normal]
  const expected = [...getFlatLines(order2).normal, ...getFlatLines(order1).normal]
  it('Expand lines and comments', () => {
    expect(
      sortLines(lines)
    ).toEqual(expected)
  })
})
