import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import { FlexGrid, FlexChild } from '../flex-grid'



export default class ScrollPanel extends PureComponent {
  constructor(props) {
    super(props)

    this.spi = null
    this.buttons = null
    this.animationTimeout = null
    this.scrollOffset = null
    this.calculated = false
    this.state = { show: false, upEnabled: true, downEnabled: true }

    this.ensureVisible = this.ensureVisible.bind(this)
  }

  arrowsEnabled() {
    let upEnabled = true
    let downEnabled = true

    if (this.spi.scrollTop === 0) {
      upEnabled = false
    }
    if (this.spi.scrollHeight - this.spi.scrollTop <= this.spi.clientHeight) {
      downEnabled = false
    }
    return { upEnabled, downEnabled }
  }

  easeInOut = (currentTime, start, change, duration) => {
    let newCurrentTime = currentTime / (duration / 2)
    if (newCurrentTime < 1) {
      return ((change / 2) * newCurrentTime * newCurrentTime) + start
    }
    newCurrentTime -= 1
    return ((-change / 2) * ((newCurrentTime * (newCurrentTime - 2)) - 1)) + start
  }

  scrollTo(element, to, duration, onEnd) {
    const originalElement = element
    const start = element.scrollTop
    const buttonSize = this.buttons.clientHeight
    const change = to ? (to + buttonSize) - start : 0
    const increment = 20

    if (this.animationTimeout != null) {
      clearTimeout(this.animationTimeout)
      this.animationTimeout = null
    }

    const animateScroll = (elapsedTime) => {
      const newElapsedTime = elapsedTime + increment
      originalElement.scrollTop = this.easeInOut(newElapsedTime, start, change, duration)
      const arrows = this.arrowsEnabled()
      if (newElapsedTime < duration && ((arrows.upEnabled && to < 0) ^ (arrows.downEnabled && to >= 0))) {
        this.animationTimeout = setTimeout(() => {
          animateScroll(newElapsedTime)
        }, increment)
      } else {
        this.animationTimeout = null
        this.scrollOffset = null
        if (onEnd) {
          onEnd()
        }
      }
    }
    animateScroll(0)
  }

  updateArrowsEnabled = () => {
    const arrows = this.arrowsEnabled()
    if (this.state.upEnabled !== arrows.upEnabled ||
      this.state.downEnabled !== arrows.downEnabled) {
      this.setState(arrows)
    }
  }

  scrollDiv = (updown) => {
    const to = this.spi.scrollTop + ((this.spi.clientHeight / 2) * ((updown === 'up') ? -1 : 1))
    this.scrollTo(this.spi, to, 60, this.updateArrowsEnabled)
  }

  showOrHide(state) {
    let mustShow = false
    const buttonsHeight = (this.buttons) ? this.buttons.clientHeight : 0
    const height = this.spi.clientHeight - buttonsHeight
    if (height && this.spi.childNodes && this.spi.childNodes.length > 0) {
      mustShow = _.some(this.spi.childNodes, (child) => child.offsetTop + child.clientHeight > height)
    }
    const arrows = this.arrowsEnabled()
    if (!arrows.upEnabled && !arrows.downEnabled) {
      mustShow = false
    }

    if (state.show !== mustShow || state.upEnabled !== arrows.upEnabled || state.downEnabled !== arrows.downEnabled) {
      this.setState({ show: mustShow, ...arrows })
    }

    this.calculated = true
  }

  ensureVisible(component) {
    const height = this.spi.clientHeight
    const top = this.spi.scrollTop
    const element = ReactDOM.findDOMNode(component) // eslint-disable-line
    if (!element) {
      return
    }
    const minTop = element.offsetTop
    const minBottom = element.offsetTop + element.clientHeight
    if (height && ((minBottom > (height + top)) || minTop < top)) {
      const newBottom = ((minBottom - height) > 0) ? (minBottom - height) : minBottom
      const scrollOffsetTemp = minBottom > (height + top) ? newBottom : minTop

      if (this.scrollOffset == null) {
        this.scrollOffset = scrollOffsetTemp
      }

      const position = [this.scrollOffset, scrollOffsetTemp]
      this.scrollOffset = minBottom > (height + top) ? _.max(position) : _.min(position)
      this.scrollTo(this.spi, this.scrollOffset, 400, this.updateArrowsEnabled)
    }
  }

  componentDidMount() {
    const { reference } = this.props
    this.showOrHide(this.state)
    this.calculated = false

    if (reference) {
      reference(this)
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevProps.children !== this.props.children) {
      this.calculated = false
    }
    if (this.calculated === false) {
      this.showOrHide(prevState)
    }

    if (!prevState.show && this.state.show) {
      this.scrollTo(this.spi, this.scrollOffset, 400, this.updateArrowsEnabled)
    }
  }

  render() {
    const {
      classes, style, styleCont, styleButtonsRoot, styleButtonsCont, styleIconUp, styleIconDown, styleButtonUp,
      styleButtonDown
    } = this.props
    const { show, upEnabled, downEnabled } = this.state
    const hiddenClass = (show) ? '' : classes.scrollPanelItemsButtonsHidden
    const downDisabledClass = (!downEnabled) ? classes.scrollPanelButtonDownDisabled : ''
    const upDisabledClass = (!upEnabled) ? classes.scrollPanelButtonUpDisabled : ''

    return (
      <FlexGrid direction={'column'} className={classes.scrollPanelRoot} style={style}>
        <FlexChild outerClassName={classes.scrollPanelItemsRoot} innerClassName={classes.scrollPanelItemsContainer}>
          <div className={`${classes.scrollPanelItems} ${hiddenClass}`}
               style={styleCont}
               ref={(el) => {
                 this.spi = el
               }}
               onScroll={() => this.showOrHide(this.state)}
          >
            {this.props.children}
          </div>
        </FlexChild>
        <div className={classes.scrollPanelButtonsRoot}
             style={{ ...styleButtonsRoot, display: (show) ? 'block' : 'none' }}
             ref={(el) => {
               this.buttons = el
             }}
        >
          <div className={classes.scrollPanelButtonsCont} style={styleButtonsCont}>
            <button key={`down_${downEnabled}`}
                    className={`${classes.scrollPanelButton} ${classes.scrollPanelButtonDown} ${downDisabledClass}`}
                    style={styleButtonDown}
                    onClick={() => this.scrollDiv('down')}
            >
              <i className={classes.scrollPanelIconDown} style={styleIconDown}/>
            </button>
            <button key={`up_${upEnabled}`}
                    className={`${classes.scrollPanelButton} ${classes.scrollPanelButtonUp} ${upDisabledClass}`}
                    style={styleButtonUp}
                    onClick={() => this.scrollDiv('up')}
            >
              <i className={classes.scrollPanelIconUp} style={styleIconUp}/>
            </button>
          </div>
        </div>
      </FlexGrid>
    )
  }
}

ScrollPanel.propTypes = {
  children: PropTypes.node,
  classes: PropTypes.object,
  style: PropTypes.object,
  styleCont: PropTypes.object,
  styleButtonsRoot: PropTypes.object,
  styleButtonsCont: PropTypes.object,
  styleButtonDown: PropTypes.object,
  styleButtonUp: PropTypes.object,
  styleIconDown: PropTypes.object,
  styleIconUp: PropTypes.object,
  reference: PropTypes.func
}

ScrollPanel.defaultProps = {
  style: {},
  styleCont: {},
  styleButtonsRoot: {},
  styleButtonsCont: {},
  styleButtonDown: {},
  styleButtonUp: {},
  styleIconDown: {},
  styleIconUp: {}
}