import React, { Component } from 'react'
import PropTypes from 'prop-types'
import styled from 'styled-components'
import { I18N } from '3s-posui/core'

import LinePropTypes from '../../../../../prop-types/LinePropTypes'
import LineValueColumnPropTypes from '../../../../../prop-types/LineValueColumnPropTypes'
import { Col, Grid, Row } from '../../../../../component/grid'
import { shallowIgnoreEquals } from '../../../../../../util/renderUtil'

const DEFAULT_INDENT = 15

const Container = styled.div`
  width: 100%;
`
const itemSpanStyle = {
  display: 'inline-block',
  textAlign: 'left',
  width: '100%',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis'
}

const itemDescrStyle = { paddingTop: '0.2vh', marginRight: '0.2vw' }

const itemTextStyle = { display: 'inline-block', textAlign: 'left', width: '90%' }

const childSpanStyle = { marginRight: '0.2vw' }

const modCommentPrefix = {
  '[OnSide]': <I18N id={'$ONSIDE'}/>,
  '[Light]': <I18N id={'$LIGHT'}/>,
  '[Extra]': <I18N id={'$EXTRA'}/>
}

const styles = {
  dontNeedCook: {
    color: '#808080',
    opacity: '0.8'
  },
  waitingCook0: {
    color: 'blue'
  },
  waitingCook1: {
    color: 'blue'
  },
  waitingCook2: {
    color: 'blue'
  },
  waitingCook3: {
    color: 'blue'
  }
}

const modQtyPrefixes = {
  '0': '$WITHOUT'
}


function getTagClassName(tag) {
  switch (tag) {
    case 'doing':
      return 'fas fa-arrow-right fa-fw test_LineItemsRenderer_DOING'
    case 'done':
    case 'served':
      return 'fas fa-check fa-fw test_LineItemsRenderer_DONE'
    case 'wait-prep-time':
      return 'far fa-clock fa-fw test_LineItemsRenderer_TIME'
    case 'hold':
      return 'fas fa-hand-paper fa-fw test_LineItemsRenderer_HOLD'
    case 'fire':
      return 'fas fa-bolt fa-fw test_LineItemsRenderer_FIRE'
    case 'dont-make':
      return 'fas fa-ban fa-fw test_LineItemsRenderer_DONTMAKE'
    case 'dont-need-cook':
      return 'fas fa-ban fa-fw test_LineItemsRenderer_DONTNEEDCOOK'
    default:
      return 'fa-fw test_LineItemsRenderer_DEFAULT'
  }
}

function GetItemSpan({ item, ident, orderState }) {
  const spacing = ident * DEFAULT_INDENT
  let comment = null
  const commentSpacing = (ident + 1) * DEFAULT_INDENT
  if (item.comments.length > 0 && item.comments[0].comment !== '') {
    comment = item.comments[0].comment
    if (modCommentPrefix[comment] != null) {
      comment = modCommentPrefix[comment]
    }
  }

  const voidedItem = item.attrs.voided.toLowerCase() === 'true'
  const spanStyle = { marginLeft: spacing }
  const itemQty = parseInt(item.attrs.qty, 10)
  if (itemQty === 0 || orderState === 'VOIDED') {
    spanStyle.textDecoration = 'line-through'
    spanStyle.color = '#808080'
  }

  return (
    <span style={itemSpanStyle}>
      <span style={spanStyle}>
        <span style={childSpanStyle}>
          {!voidedItem && modQtyPrefixes[itemQty] ? <I18N id={modQtyPrefixes[itemQty]}/> : itemQty}
        </span>
        {item.attrs.description}
      </span>
      {comment != null && (
        <span>
          <br/>
          <span style={{ marginLeft: commentSpacing }}>{comment}</span>
        </span>
      )}
    </span>
  )
}

GetItemSpan.propTypes = {
  item: PropTypes.any,
  ident: PropTypes.any,
  orderState: PropTypes.string
}


function separatePartsInColumns(parts, maxColumns) {
  const columns = []
  const numberOfColumns = parts.length === 1 ? 1 : maxColumns
  Array.from(Array(numberOfColumns).keys()).forEach(() => columns.push({ height: 0, parts: [] }))

  parts.forEach(part => {
    let minColumnIndex = -1
    columns.some((column, index) => {
      const newColumnHeight = column.height + part.size

      columns.some((innerColumn) => {
        if (newColumnHeight <= innerColumn.height) {
          minColumnIndex = index
          return true
        }

        return false
      })

      return minColumnIndex !== -1
    })

    if (minColumnIndex !== -1) {
      columns[minColumnIndex].height += part.size
      columns[minColumnIndex].parts.push(part)
      return
    }

    let minColumnHeight = -1
    columns.forEach((column, index) => {
      const newColumnHeight = column.height + part.size
      if (minColumnHeight === -1 || newColumnHeight < minColumnHeight) {
        minColumnIndex = index
        minColumnHeight = newColumnHeight
      }
    })

    columns[minColumnIndex].height += part.size
    columns[minColumnIndex].parts.push(part)
  })

  return columns
}

class LineItemsRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { column, line } = this.props
    return (
      <Container style={column.style}>
        {this.renderLineDescription(line, column.maxColumns)}
      </Container>
    )
  }

  shouldComponentUpdate(nextProps) {
    return !shallowIgnoreEquals(
      this.props,
      nextProps,
      'column')
  }

  renderLineDescription(line, maxColumns) {
    const parts = this.getItemParts(line)
    const columns = separatePartsInColumns(parts, maxColumns)
    const xs = 12 / columns.length

    return (
      <Grid fluid={true}>
        <Row>
          {columns.map((col, idx) =>
            <Col xs={xs} key={idx} columnWidth={100 / columns.length}>
              {col.parts.map(part => this.getItemDescription(part.product))}
            </Col>
          )}
        </Row>
      </Grid>
    )
  }

  getItemParts(line) {
    const items = []

    for (let i = 0; i < line.items.length; i++) {
      const item = line.items[i]
      if (item.isProduct()) {
        items.push({ product: item, size: this.getProductSize(item.items) })
      } else {
        item.items.forEach(son => {
          const sonDescription = this.getItemParts(son)
          sonDescription.forEach(desc => {
            items.push(desc)
          })
        })
      }
    }

    return items
  }

  getProductSize(product) {
    if (product.items.length === 0) {
      return 1 + product.comments.length
    } else if (product.multipliedQty === 0) {
      return 1
    }

    let size = 1 + product.comments.length
    product.items.forEach(son => {
      size += this.getProductSize(son)
    })
    return size
  }

  getItemDescription(item) {
    const itemTag = item.getLastTag()
    return (
      <Container
        key={`${item.itemId}-${item.partCode}`}
        style={{ display: 'flex', ...this.getContainerClassName(itemTag, item.qty, item.orderState) }}
      >
        <i className={getTagClassName(itemTag)} style={itemDescrStyle}/>
        {this.getItemText(item.items, null, item.orderState)}
      </Container>
    )
  }

  getContainerClassName(tag, itemQty, orderState) {
    const { currentThreshold } = this.props
    const tags = ['served', 'doing', 'done', 'wait-prep-time', 'hold', 'fire', 'dont-make', 'dont-need-cook']

    let style = {}

    if (!tags.includes(tag) && itemQty > 0 && orderState !== 'VOIDED') {
      style = { ...style, ...styles[`waitingCook${currentThreshold}`] }
    }

    if (tag === 'dont-need-cook') {
      style = { ...style, ...styles.dontNeedCook }
    }

    return style
  }

  getItemText(item, ident, orderState) {
    let currentIdent = 0
    if (ident != null) {
      currentIdent = ident
    }

    if (item.items.length === 0) {
      return <GetItemSpan item={item} ident={currentIdent} orderState={orderState} />
    }

    return (
      <div style={itemTextStyle}>
        <GetItemSpan item={item} ident={currentIdent} orderState={orderState} />
        {item.items.map((son, index) => {
          const itemText = this.getItemText(son, currentIdent + 1, orderState)
          if (itemText != null) {
            return <span key={index}><br/><span>{itemText}</span></span>
          }
          return null
        })}
      </div>
    )
  }
}

LineItemsRenderer.propTypes = {
  line: LinePropTypes,
  column: LineValueColumnPropTypes,
  currentThreshold: PropTypes.number
}

export default LineItemsRenderer
