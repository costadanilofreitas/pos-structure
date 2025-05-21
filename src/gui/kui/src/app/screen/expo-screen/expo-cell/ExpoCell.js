import { I18N } from '3s-posui/core'
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { FlexChild, FlexGrid } from '3s-widgets'
import {
  AlertIcon,
  ExpoCellContainer,
  FaIcon,
  OrderLine,
  OrderLines,
  OrderLineText,
  VoidedIcon,
  SaveIcon,
  CellBodyContainer,
  MacroContent, OrderLineTextComment,
  DeliveryObservation
} from './StyledExpoCell'
import ExpoCellHeader from './expo-cell-header'
import ExpoCellFooter from './expo-cell-footer'
import DoubleClick from './DoubleClick'
import parseMacros from '../../../../util/CellFormater'
import { shallowCompareEquals, shallowIgnoreEquals } from '../../../../util/renderUtil'


const modCommentPrefix = {
  '[OnSide]': <I18N id={'$ONSIDE'}/>,
  '[Light]': <I18N id={'$LIGHT'}/>,
  '[Extra]': <I18N id={'$EXTRA'}/>
}

function getLastTag(tags) {
  for (let i = tags.length - 1; i >= 0; i--) {
    if (tags[i] !== 'printed') {
      return tags[i]
    }
  }
  return null
}

function isUnavailable(item) {
  return item.attrs.qty === '0' || item.attrs.voided.toLowerCase() === 'true'
}

function isDelivered(item) {
  return (item.tags || []).find(tag => tag === 'delivered')
}


function getTagClassName(tag) {
  switch (tag) {
    case 'doing':
      return 'fas fa-arrow-right fa-fw test_Cell_DOING'
    case 'done':
    case 'served':
      return 'fas fa-check fa-fw test_Cell_DONE'
    case 'wait-prep-time':
      return 'far fa-clock fa-fw test_Cell_TIME'
    case 'hold':
      return 'fas fa-hand-paper fa-fw test_Cell_HOLD'
    case 'fire':
      return 'fas fa-bolt fa-fw test_Cell_FIRE'
    case 'dont-make':
      return 'fas fa-ban fa-fw test_Cell_DONTMAKE'
    case 'dont-need-cook':
      return 'fas fa-ban fa-fw test_Cell_NEEDCOOK'
    default:
      return 'fa-fw'
  }
}

function getDeliveryObservation(order) {
  const remoteOrderJson = order.props.REMOTE_ORDER_JSON
  if (remoteOrderJson) {
    const parsedJson = JSON.parse(remoteOrderJson)
    if (parsedJson.observations) {
      return true
    }
  }
  return false
}

function OrderInformation(props) {
  const { order, lines, backgroundColor, blink } = props
  const pageIndex = order.page - 1
  const startIndex = pageIndex * lines
  const endIndex = startIndex + lines
  const flexDirection = 'row'

  const getChildKey = i => `child-${i}`
  const getQuantity = (item, currentOrderState) => {
    let prefix = ''
    const itemQuantity = parseInt(item.attrs.qty, 10)
    const itemDefaultQuantity = parseInt(item.attrs.default_qty, 10)
    const orderIsCanceled = currentOrderState === 'VOIDED'

    const itemModified = itemQuantity !== itemDefaultQuantity
    if (itemModified && itemQuantity === 0) {
      prefix = '$WITHOUT'
      return { quantity: <I18N id={prefix}/>, color: orderIsCanceled ? '' : 'red' }
    } else if (itemModified && itemQuantity - itemDefaultQuantity > 0 && item.attrs.level !== '0') {
      prefix = '$ADDITIONAL'
      const quantity = <span>{itemQuantity - itemDefaultQuantity} <I18N id={prefix}/></span>
      return { quantity: quantity, color: orderIsCanceled ? '' : 'green' }
    }
    return { quantity: itemQuantity, prefix: false }
  }

  const getModifierCommentIndex = (item) => {
    for (let i = 0; i < item.comments.length; i++) {
      if (Object.keys(modCommentPrefix).indexOf(item.comments[i].comment) >= 0) {
        return i
      }
    }

    return -1
  }

  const getModifierComment = (item) => {
    const modifierCommentIndex = getModifierCommentIndex(item)
    if (modifierCommentIndex === -1) {
      return ''
    }

    const comment = item.comments[modifierCommentIndex].comment
    return modCommentPrefix[comment]
  }

  const getComment = (item) => {
    const modifierCommentIndex = getModifierCommentIndex(item)

    for (let i = 0; i < item.comments.length; i++) {
      if (i !== modifierCommentIndex) {
        return item.comments[i].comment
      }
    }

    return ''
  }

  const iconTextRate = [1, 14]
  const orderState = order.attrs.state

  let stateId

  try {
    stateId = Number(order.attrs.state_id)
  } catch {
    stateId = order.attrs.state_id
  }

  const podType = order.attrs.pod_type
  const isAlert = stateId === 1 || stateId === 3
  const isStored = stateId === 2 && podType !== 'TS'
  const isVoided = stateId === 4
  const hasIcon = isAlert || isStored || isVoided
  const cellBodyBackgroundColor = hasIcon || backgroundColor ? backgroundColor : '#d3d3d3'

  const items = order.flattenItems.slice(startIndex, endIndex).map((item, i) => {
    const itemLayout = getQuantity(item, orderState)
    const itemColor = itemLayout.color
    const itemComment = getComment(item)
    const unavailableItem = isUnavailable(item)
    const itemQuantity = !unavailableItem ? itemLayout.quantity : 0

    return (
      <FlexChild size={itemComment !== '' ? 2 : 1} key={getChildKey(i)}>
        <FlexGrid direction={flexDirection}>
          <FlexChild size={iconTextRate[0]}>
            <FaIcon className={getTagClassName(getLastTag(item.tags || []))}/>
          </FlexChild>
          <OrderLines backgroundColor={cellBodyBackgroundColor} size={iconTextRate[1]}>
            <OrderLine
              className={`test_KdsCell_ORDER-LINE ${itemQuantity} ${item.attrs.description} LV${item.attrs.level}`}
              unavailable={unavailableItem}
              delivered={isDelivered(item)}
              level={item.attrs.level}
              itemColor={itemColor}
              blink={blink}
            >
              <OrderLineText>
                {getModifierComment(item)} {itemQuantity} {item.attrs.description}
              </OrderLineText>
            </OrderLine>
            {itemComment !== '' &&
            <OrderLine
              level={item.attrs.level}
              className={`${itemQuantity} ${item.attrs.description} LV${item.attrs.level + 1}`}
              unavailable={unavailableItem}
              isComment={true}
            >
              <OrderLineTextComment>* {itemComment}</OrderLineTextComment>
            </OrderLine>
            }
          </OrderLines>
        </FlexGrid>
      </FlexChild>
    )
  })

  const filler = Array.from({ length: lines - items.length })
    .map((e, i) => (<FlexChild size={1} key={getChildKey(lines + i)}/>))

  const hasDeliveryObservation = getDeliveryObservation(order)
  return (
    <FlexGrid direction={'column'}>
      <CellBodyContainer
        backgroundColor={cellBodyBackgroundColor}
        className={'test_ExpoCell_BODY'}
        blink={blink}
      >
        {hasDeliveryObservation && order.page === 1 &&
          <FlexChild size={1} key={'obs'}>
            <FlexGrid direction={'row'}>
              <FlexChild size={1}>
                <DeliveryObservation>
                  <i className={'fas fa-exclamation'}/>
                  &nbsp;
                  <I18N id={'$OBSERVATION_DELIVERY'}/>
                </DeliveryObservation>
              </FlexChild>
            </FlexGrid>
          </FlexChild>
        }
        {items.concat(filler)}
      </CellBodyContainer>
    </FlexGrid>
  )
}

OrderInformation.propTypes = {
  order: PropTypes.object,
  lines: PropTypes.number,
  backgroundColor: PropTypes.string,
  blink: PropTypes.bool
}

export default class ExpoCell extends Component {
  constructor(props) {
    super(props)
    this.state = { refresh: null }
    this.thresholdTimer = null
    this.autoCommandTimer = null
  }

  shouldComponentUpdate(nextProps, nextState) {
    const { settings: { onSellClick } } = this.props.kdsModel

    if (this.state.refresh !== nextState.refresh) {
      return true
    }

    if (!shallowIgnoreEquals(this.props.kdsModel.layout, nextProps.kdsModel.layout)) {
      return true
    }

    if (!shallowIgnoreEquals(this.props.kdsModel.cellFormat, nextProps.kdsModel.cellFormat)) {
      return true
    }

    if (onSellClick !== nextProps.kdsModel.settings.onSellClick) {
      return true
    }
    const kdsModelProps = ['showItems', 'coloredArea', 'autoOrderCommand', 'thresholds']
    if (!shallowCompareEquals(this.props.kdsModel, nextProps.kdsModel, ...kdsModelProps)) {
      return true
    }

    if (nextProps.order) {
      if (!this.props.order) {
        return true
      }
      if (!shallowCompareEquals(this.props.order, nextProps.order, 'items', 'pages', 'page')) {
        return true
      }
      const orderAttrsProps = ['order_id', 'display_time', 'display_time_gmt', 'prod_state', 'state_id']
      if (!shallowCompareEquals(this.props.order.attrs, nextProps.order.attrs, ...orderAttrsProps)) {
        return true
      }
    } else if (this.props.order) {
      return true
    }

    return !shallowCompareEquals(this.props, nextProps, 'row', 'col', 'selected')
  }

  removeAutoCommandTimer() {
    if (this.autoCommandTimer) {
      clearTimeout(this.autoCommandTimer)
      this.autoCommandTimer = null
    }
  }

  removeThresholdTimer() {
    if (this.thresholdTimer) {
      clearTimeout(this.thresholdTimer)
      this.thresholdTimer = null
    }
  }

  getAutoOrderCommand() {
    const { autoOrderCommand } = this.props.kdsModel
    if (!autoOrderCommand) {
      return { time: 0, command: '' }
    }
    return autoOrderCommand
  }

  getAutoCommandTime(order) {
    const { time: commandTime } = this.getAutoOrderCommand()
    const currentOrderTime = this.getOrderTimeOnExpo(order)
    return Math.max(commandTime - currentOrderTime, 0)
  }

  getMinThresholdTime(order) {
    const { thresholds } = this.props.kdsModel
    const currentOrderTime = this.getOrderTimeOnExpo(order)
    let thresholdTimer = null
    thresholds.forEach(({ time }) => {
      if (thresholdTimer) {
        return
      }
      const timeDiff = time - currentOrderTime
      if (timeDiff > 0) {
        thresholdTimer = timeDiff
      }
    })
    return thresholdTimer
  }
  autoCommandHandler = () => {
    const { executeBumpCommand, order, kdsModel: { autoOrderCommand: { command } } } = this.props
    executeBumpCommand(command, order.attrs.order_id)
    this.autoCommandTimer = null
  }

  setAutoCommandTimeout(order) {
    const { command } = this.getAutoOrderCommand()
    if (!command) {
      return
    }
    this.removeAutoCommandTimer()
    const time = this.getAutoCommandTime(order)
    if (isNaN(time)) {
      return
    }
    this.autoCommandTimer = setTimeout(this.autoCommandHandler, time * 1000)
  }

  thresholdHandler = () => {
    this.setState({ refresh: !this.state.refresh })
  }

  setThresholdTimeout(order) {
    this.removeThresholdTimer()
    const time = this.getMinThresholdTime(order)
    if (time) {
      this.thresholdTimer = setTimeout(this.thresholdHandler, time * 1000)
    }
  }

  componentWillUnmount() {
    this.removeThresholdTimer()
    this.removeAutoCommandTimer()
  }

  shouldColorHeader() {
    return this.props.kdsModel.coloredArea.includes('header')
  }

  shouldColorBody() {
    return this.props.kdsModel.coloredArea.includes('body')
  }

  shouldColorFooter() {
    return this.props.kdsModel.coloredArea.includes('footer')
  }

  shouldColorTimer() {
    return this.props.kdsModel.coloredArea.includes('timer')
  }

  getBorderColor(saleType) {
    const { theme } = this.props
    if (saleType.toUpperCase() === 'TAKE_OUT') {
      return theme.takeOutColorBorder
    }
    if (saleType.toUpperCase() === 'DELIVERY') {
      return theme.deliveryColorBorder
    }
    return theme.backgroundColor
  }

  getBorderValues() {
    const { kdsModel, order } = this.props
    const totalCol = kdsModel.layout.cols
    const firstPage = order.page === 1
    const lastPage = order.page === order.pages

    let cellWithBorder = false
    let removeBorderLeft = false
    let removeBorderRight = false
    let headerBorderRadius = '1vmin 1vmin 0vmin 0vmin'
    let footerBorderRadius = '0vmin 0vmin 1vmin 1vmin'
    let widthSize = '100%'

    if (order.pages === 1 || order.pages === 2 || (order.pages >= 3 && (firstPage || lastPage))) {
      cellWithBorder = true
    }
    if (order.pages > 1) {
      if (firstPage) {
        removeBorderRight = true
        widthSize = this.props.col + 1 === totalCol ? 'calc(100% - 0.5vmin)' : 'calc(100% - 0.4vmin)'
        headerBorderRadius = '1vmin 0vmin 0vmin 0vmin'
        footerBorderRadius = '0vmin 0vmin 0vmin 1vmin'
      }
      if (lastPage) {
        removeBorderLeft = true
        widthSize = 'calc(100% - 0.6vmin)'
        headerBorderRadius = '0vmin 1vmin 0vmin 0vmin'
        footerBorderRadius = '0vmin 0vmin 1vmin 0vmin'
      }
    }
    if (order.pages === 1) {
      widthSize = 'calc(100% - 1vmin)'
    }
    if (order.pages >= 3 && !firstPage && !lastPage) {
      headerBorderRadius = 'none'
      footerBorderRadius = 'none'
      if (this.props.col + 1 === totalCol) {
        widthSize = 'calc(100% - 0.1vmin)'
      }
    }

    return {
      cellWithBorder: cellWithBorder,
      removeBorderRight: removeBorderRight,
      removeBorderLeft: removeBorderLeft,
      headerBorderRadius: headerBorderRadius,
      footerBorderRadius: footerBorderRadius,
      widthSize: widthSize
    }
  }

  getBackgroundColor(stateId, isVoided, isInProgress, colors, orderThreshold) {
    const { order, selected, theme } = this.props
    const podType = order.attrs.pod_type
    const isStored = stateId === 2 && podType !== 'TS'
    const isTotaled = stateId === 3

    if (isVoided || isInProgress || isStored || isTotaled) {
      if (this.shouldColorHeader() || this.shouldColorFooter()) {
        return selected ? theme.activeExpoCellColor : theme.expoDefaultColor
      }
      return 'none'
    }
    if (order.attrs.recalled.toLowerCase() === 'true') {
      return theme.recalledCellBackground
    }
    if (this.shouldColorTimer()) {
      return colors[orderThreshold] !== '#undefined' ? colors[orderThreshold] : theme.fontColor
    }
    return colors[orderThreshold] !== '#undefined' ? colors[orderThreshold] : theme.expoCellColor
  }

  getCurrentThreshold(order, thresholds) {
    const orderTimeOnExpo = this.getOrderTimeOnExpo(order)

    let orderThreshold = 0
    thresholds.forEach(threshold => orderTimeOnExpo > (threshold.time - 0.1) ? orderThreshold++ : null)

    const lastThresholdIndex = thresholds.length - 1
    return orderThreshold <= lastThresholdIndex ? orderThreshold : lastThresholdIndex
  }

  render() {
    const { kdsModel, order, selected, setCurrentOrder, index, executeBumpCommand, theme } = this.props

    if (!order) {
      return null
    }

    let stateId
    try {
      stateId = Number(order.attrs.state_id)
    } catch {
      stateId = order.attrs.state_id
    }

    const thresholds = kdsModel.thresholds
    const colors = thresholds.map(threshold => threshold.color)
    const colorTimer = this.shouldColorTimer()
    if (colorTimer) {
      colors.unshift(selected ? theme.expoActiveFontColor : theme.expoFontColor)
    }
    const lines = kdsModel.layout.lines
    const orderThreshold = this.getCurrentThreshold(order, thresholds)
    const borderValues = this.getBorderValues()
    const isInProgress = stateId === 1
    const isVoided = stateId === 4
    const isReady = !!order.attrs.tagged_timestamp
    const cellMustBlink = isReady && (!isVoided && !isInProgress)
    const shouldColorHeader = this.shouldColorHeader()
    const shouldColorBody = this.shouldColorBody()
    const shouldColorFooter = this.shouldColorFooter()
    const backgroundColor = this.getBackgroundColor(stateId, isVoided, isInProgress, colors, orderThreshold)
    const cellClasses = `threshold_${orderThreshold} canceledOrder_${isVoided.toString()} ` +
      `all_ready_${cellMustBlink.toString()}`
    const select = () => {
      setCurrentOrder(index)
    }
    const doubleClick = () => {
      setCurrentOrder(index)
      executeBumpCommand(kdsModel.settings.onSellClick, order.attrs.order_id)
    }

    this.setThresholdTimeout(order)
    this.setAutoCommandTimeout(order)

    return (
      <DoubleClick onClick={select} onDoubleClick={doubleClick}>
        <ExpoCellContainer
          className={`test_KdsCell_CONTAINER ${this.props.row}x${this.props.col} ${cellClasses}`}
          selected={selected}
          blink={cellMustBlink}
          fontSizeZoom={kdsModel.layout.fontsize}
          theme={theme}
          withBorder={borderValues.cellWithBorder}
          widthSize={borderValues.widthSize}
          removeBorderLeft={borderValues.removeBorderLeft}
          removeBorderRight={borderValues.removeBorderRight}
          borderColor={this.getBorderColor(order.attrs.sale_type)}
        >
          <FlexGrid direction={'column'}>
            <FlexChild size={1}>
              <ExpoCellHeader
                order={order}
                format={kdsModel.cellFormat.header}
                selected={selected}
                blink={cellMustBlink}
                borderRadius={borderValues.headerBorderRadius}
                backgroundColor={shouldColorHeader ? backgroundColor : null}
                timerColor={colorTimer ? backgroundColor : null}
                theme={theme}
              />
            </FlexChild>
            <FlexChild size={lines - 1}>
              {this.renderBody(
                stateId,
                shouldColorBody ? backgroundColor : null,
                lines,
                select,
                doubleClick,
                cellMustBlink)
              }
            </FlexChild>
            <FlexChild size={1}>
              <ExpoCellFooter
                order={order}
                blink={cellMustBlink}
                format={kdsModel.cellFormat.footer}
                selected={selected}
                borderRadius={borderValues.footerBorderRadius}
                backgroundColor={shouldColorFooter ? backgroundColor : null}
              />
            </FlexChild>
          </FlexGrid>
        </ExpoCellContainer>
      </DoubleClick>
    )
  }

  renderBody(stateId, backgroundColor, lines, select, doubleClick, cellMustBlink) {
    const { kdsModel, order, theme } = this.props
    const podType = order.attrs.pod_type
    const invalidBgColor = [theme.activeExpoCellColor, theme.expoCellColor]
    if (!kdsModel.showItems) {
      return (
        <DoubleClick onClick={select} onDoubleClick={doubleClick}>
          <MacroContent
            fontSizeZoom={kdsModel.layout.fontsize}
            backgroundColor={invalidBgColor.includes(backgroundColor) ? 'none' : backgroundColor}
          >
            <div>
              {parseMacros(kdsModel.cellFormat.body, order, null)}
            </div>
          </MacroContent>
        </DoubleClick>
      )
    }

    const isInProgress = stateId === 1 || stateId === 3
    const isStored = stateId === 2 && podType !== 'TS'
    const isVoided = stateId === 4

    return <>
      {isVoided && <VoidedIcon fontSizeZoom={kdsModel.layout.fontsize} className="fas fa-times"/>}
      {isInProgress && <AlertIcon fontSizeZoom={kdsModel.layout.fontsize} className="fas fa-exclamation-triangle"/>}
      {isStored && <SaveIcon fontSizeZoom={kdsModel.layout.fontsize} className="fas fa-save"/>}
      <OrderInformation
        backgroundColor={invalidBgColor.includes(backgroundColor) ? 'none' : backgroundColor}
        order={order}
        lines={lines}
        blink={cellMustBlink}
      />
    </>
  }

  getOrderTimeOnExpo(order) {
    const { timeDelta } = this.props
    let orderTime = order.attrs.display_time_gmt
    if (!orderTime) {
      orderTime = order.attrs.display_time
    }
    return ((new Date() - new Date(new Date(orderTime).getTime())) + timeDelta) / 1000
  }
}

ExpoCell.propTypes = {
  kdsModel: PropTypes.object,
  order: PropTypes.object,
  row: PropTypes.number,
  col: PropTypes.number,
  selected: PropTypes.bool,
  index: PropTypes.number,
  timeDelta: PropTypes.number,
  setCurrentOrder: PropTypes.func,
  executeBumpCommand: PropTypes.func,
  theme: PropTypes.object
}
