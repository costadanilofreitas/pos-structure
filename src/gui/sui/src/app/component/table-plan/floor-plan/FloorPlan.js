import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'

import BarChair from './BarChair'
import Plant from './Plant'
import Rectangle4S from './Rectangle4S'
import Rectangle8S from './Rectangle8S'
import Sofa4SH from './Sofa4SH'
import Sofa4SV from './Sofa4SV'
import Square2SH from './Square2SH'
import Square2SV from './Square2SV'
import Square4S from './Square4S'
import TabsShortcut from './TabsShortcut'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  floorPlanRoot: {
    composes: 'floor-plan-root',
    position: 'relative',
    overflow: 'hidden',
    width: '100%',
    height: '100%'
  },
  floorPlanCont: {
    composes: 'floor-plan-cont',
    position: 'absolute'
  },
  floorPlanRotated: {
    composes: 'floor-plan-rotated',
    position: 'relative',
    width: '100%',
    height: '100%'
  },
  floorPlanElement: {
    composes: 'floor-plan-element',
    position: 'absolute'
  },
  floorPlanItemCont: {
    composes: 'floor-plan-item-cont',
    position: 'relative',
    display: 'inline',
    whiteSpace: 'nowrap'
  },
  floorPlanTableNumber: {
    composes: 'floor-plan-table-number',
    display: 'flex',
    width: '100%',
    height: '100%',
    position: 'absolute',
    color: 'black',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1
  }
}

class FloorPlan extends PureComponent {
  state = {
    visibility: 'hidden',
    availableWidth: 0,
    availableHeight: 0
  }
  contRef = null

  getItem = (element, fill, stroke, invertAxes) => {
    const combinedProps = (!invertAxes) ?
      element.itemProps || {} :
      { ...(element.itemProps || {}), ...(element.itemPropsRotated || {}) }
    const props = {
      ...((stroke) ? { stroke } : {}),
      ...((fill) ? { fill } : {}),
      ...combinedProps
    }
    switch (_.toLower(element.type)) {
      case 'rectangle8s':
        return <Rectangle8S {...props} />
      case 'rectangle4s':
        return <Rectangle4S {...props} />
      case 'sofa4sh':
        return <Sofa4SH {...props} />
      case 'sofa4sv':
        return <Sofa4SV {...props} />
      case 'square2sh':
        return <Square2SH {...props} />
      case 'square2sv':
        return <Square2SV {...props} />
      case 'square4s':
        return <Square4S {...props} />
      case 'barchair':
        return <BarChair {...props} />
      case 'tabsshortcut':
        return <TabsShortcut {...props} />
      case 'plant':
        return <Plant {...props} />
      case 'box':
      default:
    }

    return <div {...props}> {element.text} </div>
  }

  handleTableClick = (element) => () => {
    const { onTableClick } = this.props

    if (onTableClick) {
      onTableClick(element)
    }
  }

  handleRef = (element) => {
    if (element) {
      this.contRef = element
      this.updateDimensions()
    }
  }

  updateDimensions = (visibility) => {
    if (!this.contRef) {
      return
    }
    const { availableWidth, availableHeight } = this.state
    const rect = this.contRef.getBoundingClientRect()
    const w = rect.width
    const h = rect.height
    if (availableWidth !== w || availableHeight !== h || visibility) {
      this.setState({
        availableWidth: w,
        availableHeight: h,
        ...((visibility) ? { visibility } : {})
      })
    }
  }

  componentDidMount() {
    window.addEventListener('resize', this.updateDimensions)
    _.defer(this.updateDimensions, 'visible')
  }

  componentWillUnmount() {
    this.contRef = null
    window.removeEventListener('resize', this.updateDimensions)
  }

  render() {
    const { visibility, availableWidth, availableHeight } = this.state
    const { classes, className, options, plan, rotation, tableStatus } = this.props
    const styleCont = options.styleCont || {}
    const fillColors = options.fillColors || {}
    const strokeColors = options.strokeColors || {}

    const divTextStyle = {
      width: '100%',
      height: '100%',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center'
    }

    let baseWidth = options.baseWidth
    let baseHeight = options.baseHeight

    let tableNumberStyle = {}
    if (rotation) {
      tableNumberStyle = { transform: `rotate(-${rotation}deg)` }
    }
    let xlateX = 0
    let xlateY = 0
    let contTop = 0
    let contLeft = 0
    let contWidth
    let contHeight

    const invertAxes = (rotation === 90 || rotation === 270)
    if (invertAxes) {
      const tmpWidth = baseWidth
      // noinspection JSSuspiciousNameCombination
      baseWidth = baseHeight
      // noinspection JSSuspiciousNameCombination
      baseHeight = tmpWidth
    }

    const baseRatio = baseWidth / baseHeight
    const spaceRatio = availableWidth / availableHeight
    if (baseRatio > spaceRatio) {
      contWidth = availableWidth
      contHeight = availableWidth / (baseWidth / baseHeight)
      contTop = (availableHeight - contHeight) / 2.0
    } else {
      contHeight = availableHeight
      contWidth = availableHeight / (baseHeight / baseWidth)
      contLeft = (availableWidth - contWidth) / 2.0
    }

    if (invertAxes) {
      xlateX = -((contHeight - contWidth) / 2.0)
      xlateY = -((contWidth - contHeight) / 2.0)
    }

    return (
      <div
        ref={this.handleRef}
        className={`${classes.floorPlanRoot} ${className}`}
        style={{ ...(options.style || {}), visibility }}
      >
        <div
          className={classes.floorPlanCont}
          style={{
            top: contTop,
            left: contLeft,
            width: contWidth,
            height: contHeight,
            ...(styleCont || {})
          }}
        >
          <div
            className={classes.floorPlanRotated}
            style={{ transform: `rotate(${rotation}deg) translate(${xlateX}px, ${xlateY}px)` }}
          >
            {_.map(plan, (element, idx) => {
              const isTable = Boolean(element.tableId)
              const key = `${element.type}_${idx}_${(isTable) ? element.tableId : 'none'}`
              const status = tableStatus[element.tableId]
              const fill = fillColors[status]
              const stroke = strokeColors[status]
              const width = `${(element.w / baseWidth) * 100.0}%`
              const height = `${(element.h / baseHeight) * 100.0}%`
              const left = `${(element.x / baseWidth) * 100.0}%`
              const top = `${(element.y / baseHeight) * 100.0}%`
              return (
                <div
                  key={key}
                  className={classes.floorPlanElement}
                  onClick={(isTable) ? this.handleTableClick(element) : null}
                  style={{
                    width,
                    height,
                    top,
                    left,
                    ...(element.style || {})
                  }}
                >
                  {isTable &&
                    <div
                      className={`${classes.floorPlanTableNumber} test_FloorPlan_${element.tableId.toUpperCase()}`}
                      style={tableNumberStyle}
                    >
                      {element.tableId === 'tabs' ? '' : element.tableId}
                    </div>
                  }
                  <div style={element.text != null ? divTextStyle : {}} className={classes.floorPlanItemCont}>
                    {this.getItem(element, fill, stroke, invertAxes)}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    )
  }
}

FloorPlan.propTypes = {
  classes: PropTypes.object,
  className: PropTypes.string,
  rotation: PropTypes.oneOf([0, 90, 180, 270]),
  tableStatus: PropTypes.object,
  onTableClick: PropTypes.func,
  options: PropTypes.shape({
    style: PropTypes.object,
    styleCont: PropTypes.object,
    baseWidth: PropTypes.number,
    baseHeight: PropTypes.number,
    fillColors: PropTypes.object,
    strokeColors: PropTypes.object
  }),
  plan: PropTypes.arrayOf(PropTypes.shape({
    type: PropTypes.string,
    tableId: PropTypes.string,
    itemProps: PropTypes.object,
    itemPropsRotated: PropTypes.object,
    x: PropTypes.number,
    y: PropTypes.number,
    w: PropTypes.number,
    h: PropTypes.number,
    style: PropTypes.object
  }))
}

FloorPlan.defaultProps = {
  className: '',
  rotation: 0,
  tableStatus: {},
  options: {
    style: {},
    styleCont: {},
    baseWidth: 1024,
    baseHeight: 768,
    fillColors: {},
    strokeColors: {}
  }
}

export default injectSheet(styles)(FloorPlan)
