import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'
import memoize from 'memoize-one'
import Color from 'color'

import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import shallowEqual from 'react-redux/lib/utils/shallowEqual'

import { I18N } from '3s-posui/core'
import { executeAction, executeActionProcessed } from '3s-posui/actions'
import MessageBusPropTypes from '../../prop-types/MessageBusPropTypes'
import withExecuteActionMessageBus from '../../util/withExecuteActionMessageBus'
import styles from './JssButton'


jss.setup({ insertionPoint: 'posui-css-insertion-point' })

/**
 * Button widget that allows to execute remote or local actions on the POS.
 * It provides an automatic feedback while the button is pressed by darkening the background color.
 *
 * Button style is customized via `style` property, but you can also use the available class names
 * as defined in the below. It is recommended to wrap the button on a container `<div>` in
 * order to shape the size according to your needs, otherwise you will need to override default
 * `width` and `height` that is set to `100%` by default.
 *
 * ![Button example](./buttons-example.png)
 *
 * Button allows nested common.
 *
 * ![Button tender example](./button-tender-example.png)
 *
 * In order to use this component, your app state must expose the following state:
 * - `actionRunning` using `mwActionReducer` reducer
 * This state is used to guarantee that only one action is running at a time, and block further
 * click on other button instances.
 *
 * Available class names:
 * - root element: `button-root`
 * - added when rounded property is active: `button-rounded`
 * - added when featured ribbon property is active: `button-featured`
 * - featured ribbon icon: `button-featured-ribbon`
 * - added when unavailable property is active: `button-unavailable`
 * - unavailable cross icon: `button-unavailable-cross`
 * - popup menu arrow icon: `button-popup-arrow`
 * - added to popup icon when menu opened: `button-menu-arrow-down`
 * - added to popup icon when menu closed: `button-menu-arrow-up`
 * - added when button is disabled: `button-disabled`
 */
class Button extends Component {
  constructor(props) {
    super(props)
    this.button = null
    this.localActionId = []
    this.buttonStyle = {}
    this.buttonStylePressed = {}
    this.arrowStyle = {}
    this.arrowStylePressed = {}
    this.buttonClass = ''
    this.buttonClassPressed = ''
    this.alive = true
    this.state = {
      pressed: true,
      running: false,
      timeoutOn: false
    }
    this.setActionBlocking(props)
  }

  setActionBlocking = (props) => {
    this.actionBlocking = props.blockOnActionRunning
    if (this.actionBlocking === null) {
      this.actionBlocking = props.defaultActionBlocking
    }
  }

  genStylesMemo = (
    button, style, stylePressed, styleDisabled, styleArrow, styleArrowPressed, className,
    classNamePressed, classNameDisabled, classes, rounded, featuredRibbon, unavailable, disabled, timeoutOn
  ) => {
    const isDisabled = disabled || timeoutOn
    if (!button) {
      return
    }
    // generate classes
    const buttonClass = (isDisabled) ? [classes.buttonRoot] : [classes.buttonRoot, className]
    if (rounded) {
      buttonClass.push(classes.buttonRounded)
    }
    if (featuredRibbon) {
      buttonClass.push(classes.buttonFeatured)
    }
    if (unavailable) {
      buttonClass.push(classes.buttonUnavailable)
    }
    if (isDisabled) {
      buttonClass.push(classNameDisabled)
      buttonClass.push(classes.buttonDisabled)
    }
    this.buttonClass = buttonClass.join(' ')
    buttonClass.splice(2, 0, classNamePressed)
    this.buttonClassPressed = buttonClass.join(' ')
    // background color
    this.button.className = this.buttonClass
    const computedStyle = this.getStyle(this.button)
    let backgroundColor = computedStyle.backgroundColor
    if (style.backgroundColor) {
      // style overrides computed by the class
      backgroundColor = style.backgroundColor
    }
    if (backgroundColor === 'ButtonFace') {
      backgroundColor = 'white'
    }
    const backgroundColorPressed = (new Color(backgroundColor)).darken(0.3).rgb().string()
    let color = 'black'
    if (this.props.children || this.props.text) {
      color = this.chooseContrastColor(backgroundColor)
    }
    if (!isDisabled) {
      this.buttonStyle = {
        color,
        ...style,
        backgroundColor
      }
      this.buttonStylePressed = {
        color,
        ...style,
        ...stylePressed,
        backgroundColor: backgroundColorPressed
      }
    } else {
      this.buttonStyle = {
        ...styleDisabled
      }
      this.buttonStylePressed = {
        ...styleDisabled
      }
    }

    this.arrowStyle = {
      color: this.buttonStyle.color,
      ...styleArrow
    }

    this.arrowStylePressed = {
      color: this.buttonStylePressed.color,
      ...styleArrowPressed
    }
  }
  genStyles = memoize(this.genStylesMemo)

  /**
   * Get element computed style
   */
  getStyle = (element) => {
    // almost every browser
    if (window.getComputedStyle) {
      return window.getComputedStyle(element)
    }
    // IE fallback
    return element.currentStyle
  }

  /**
   * Check if two given colors are the same
   */
  colorEquals = (color1, color2) => {
    const newColor1 = new Color(color1)
    const newColor2 = new Color(color2)
    return (newColor1.rgb()
      .string()) === (newColor2.rgb()
      .string())
  }

  mouseEnter = (evt) => {
    const { actionRunning } = this.props
    // block when an action is running
    if (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning)) {
      return
    }
    // check if button is pressed
    if (evt.buttons === 1 && !(this.props.disabled || this.state.timeoutOn)) {
      this.setPressed()
    }
    evt.stopPropagation()
    evt.preventDefault()
  }

  mouseLeave = (evt) => {
    const { pressed } = this.state
    const { actionRunning } = this.props
    // block when an action is running
    if (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning)) {
      return
    }
    if (pressed) {
      this.setState({ pressed: false })
    }
    if (evt && evt.stopPropagation) {
      evt.stopPropagation()
      evt.preventDefault()
    }
  }

  mouseDown = (evt) => {
    const { actionRunning } = this.props
    const { running } = this.state
    // block when an action is running
    if (running || (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning))) {
      return
    }
    if (!(this.props.disabled || this.state.timeoutOn)) {
      // note that disabled buttons does not receives mouse enter/leave events, so
      // we cannot change the color here
      this.setPressed()
    }
    evt.stopPropagation()
    evt.preventDefault()
  }

  mouseUp = (evt) => {
    const { actionRunning } = this.props
    // block when an action is running
    if (this.state.running || (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning))) {
      return
    }
    if (this.props.onClick) {
      this.setState({ running: true })
      Promise.resolve(this.props.onClick())
        .finally(() => {
          if (!this.alive) {
            return
          }
          this.setState({ running: false })
        })
    } else if (this.props.executeAction) {
      let params
      if (typeof (this.props.executeAction) === 'function') {
        params = this.props.executeAction()
      } else {
        params = this.props.executeAction
      }
      if (params && params.length) {
        if (this.props.blockOnActionRunning) {
          const msgBus = this.props.msgBus
          const msgBusAction = msgBus.syncAction.bind(msgBus)

          const actionName = params[0]
          const actionParameters = _.cloneDeep(params)
          actionParameters.shift()
          msgBusAction(actionName, ...actionParameters)
            .then(data => {
              if (this.props.onActionFinish) {
                try {
                  this.props.onActionFinish(data)
                } catch (e) {
                  console.error('Error while running onActionFinish callback')
                  console.error(e)
                }
              }
            })
            .catch((e) => {
              console.error('Error while running onActionFinish callback')
              console.error(e)
            })
        } else {
          let localActionId = null
          if (this.props.onActionFinish) {
            // we need to track the response
            localActionId = _.uniqueId('action_')
            this.localActionId.push(localActionId)
          }
          this.props.doExecuteAction(localActionId, ...params)
          return
        }
      } else if (typeof (this.props.executeAction) === 'function') {
        console.warn('Button received a function on "executeAction" that does not return an action.')
      }
    }
    this.mouseLeave(evt, null, true)
  }

  setPressed() {
    const { pressed } = this.state
    if (!pressed) {
      this.setState({ pressed: true })
    }
  }

  chooseContrastColor = (color) => {
    return ((new Color(color)).luminosity() > 0.179) ? '#000000' : '#FFFFFF'
  }

  static getDerivedStateFromProps(props, state) {
    let timeoutOn = false

    if (props.dialogs && props.dialogs.length > 0) {
      for (let i = 0; i < props.dialogs.length; i++) {
        if (props.dialogs[i].id === 'timeout_id') {
          timeoutOn = true
          break
        }
      }
    }

    return { ...state, timeoutOn: timeoutOn }
  }

  componentDidUpdate(prevProps) {
    const nextProps = this.props
    if ((nextProps.blockOnActionRunning !== prevProps.blockOnActionRunning) ||
      (nextProps.defaultActionBlocking !== prevProps.defaultActionBlocking)) {
      this.setActionBlocking(nextProps)
    }
    if (nextProps.actionRunning === prevProps.actionRunning) {
      return
    }
    // check if asynchronous action is finished and we need to fire executeActionProcessed
    const hasActions = !_.isEmpty(nextProps.actionRunning)
    if (hasActions && this.localActionId.length > 0) {
      const matchedActions = _.intersection(_.keys(nextProps.actionRunning), this.localActionId)
      if (matchedActions.length > 0) {
        _.forEach(matchedActions, (localActionId) => {
          const actionData = nextProps.actionRunning[localActionId]
          if (!actionData.inProgress) {
            try {
              prevProps.onActionFinish(actionData.data)
            } catch (e) {
              console.error('Error while running onActionFinish callback')
              console.error(e)
            }
            // now we can remove this action from actionRunning
            prevProps.executeActionProcessed(localActionId)
            const idx = _.indexOf(this.localActionId, localActionId)
            if (idx !== -1) {
              this.localActionId.splice(idx, 1)
            }
          }
        })
      }
    }
    const { pressed } = this.state
    if (pressed && (!nextProps.executeAction || !hasActions)) {
      this.setState({ pressed: false })
    }
  }

  shouldComponentUpdate(nextProps, nextState) {
    const eqProps = shallowEqual(this.props, nextProps)
    const eqState = shallowEqual(this.state, nextState)
    const shouldUpdate = !(eqProps && eqState)
    if (shouldUpdate && eqState) {
      const ignoreProps = ['actionRunning', 'onClick', 'executeAction', 'onActionFinish', 'dialogs']
      let ignoreUpdate = false
      _.forEach(_.keys(this.props), (key) => {
        const eq = shallowEqual(this.props[key], nextProps[key])
        if (!eq) {
          if (_.includes(ignoreProps, key)) {
            ignoreUpdate = true
          } else {
            ignoreUpdate = false
            return false
          }
        }
        return true
      })
      if (ignoreUpdate) {
        return false
      }
    }
    return shouldUpdate
  }

  componentDidMount() {
    const { timeoutOn } = this.state
    const {
      style, stylePressed, styleDisabled, className, classNamePressed, classNameDisabled,
      styleArrow, styleArrowPressed, classes, rounded, featuredRibbon, unavailable, disabled
    } = this.props
    this.genStyles(
      this.button, style, stylePressed, styleDisabled, styleArrow, styleArrowPressed, className,
      classNamePressed, classNameDisabled, classes, rounded, featuredRibbon, unavailable, disabled, timeoutOn
    )
    // text for logging purposes
    if (this.props.suppressLogging) {
      this.text = 'suppressed'
    } else if (_.isArray(this.props.children)) {
      this.text = ''
      this.props.children.map((el) => {
        if (el && el.key) {
          this.text += `${el.key} `
        }
        return null
      })
    } else if (this.props.text) {
      this.text = this.props.text
    } else {
      this.text = String(this.props.children)
    }
    // force re-render after style calculation
    this.setState({ pressed: false })
  }

  buttonRef = (ref) => {
    const { buttonElement } = this.props

    if (ref) {
      this.button = ref
      if (buttonElement) {
        buttonElement(ref)
      }
    }
  }

  componentWillUnmount() {
    const { actionRunning } = this.props
    // check if asynchronous action is finished and we need to fire executeActionProcessed
    const hasActions = !_.isEmpty(actionRunning)
    const matchedActions = _.intersection(_.keys(actionRunning), this.localActionId)
    if (this.localActionId.length > 0 && hasActions && matchedActions.length > 0) {
      _.forEach(matchedActions, (localActionId) => {
        // need to cleanup actionRunning, nobody will receive the response!
        console.warn(`Unmounting button that initiated action ${localActionId}, nobody will receive the response`)
        this.props.executeActionProcessed(localActionId)
      })
      this.localActionId = []
    }
    this.alive = false
  }

  render() {
    const { pressed, timeoutOn } = this.state
    const {
      style, stylePressed, styleDisabled, styleArrow, styleArrowPressed, className,
      classNamePressed, classNameDisabled, classes, rounded, featuredRibbon, unavailable, disabled,
      text, defaultText
    } = this.props
    this.genStyles(
      this.button, style, stylePressed, styleDisabled, styleArrow, styleArrowPressed, className,
      classNamePressed, classNameDisabled, classes, rounded, featuredRibbon,
      unavailable, disabled, timeoutOn
    )
    const translate = text && _.startsWith(text, '$')
    return (
      <button
        ref={this.buttonRef}
        className={(pressed) ? this.buttonClassPressed : this.buttonClass}
        disabled={disabled || timeoutOn}
        onMouseEnter={this.mouseEnter}
        onMouseLeave={this.mouseLeave}
        onMouseUp={this.mouseUp}
        onMouseDown={this.mouseDown}
        style={(pressed) ? this.buttonStylePressed : this.buttonStyle}
      >
        {this.renderMenuArrow()}
        {this.renderPopupArrow()}
        {this.renderFeaturedRibbon()}
        {this.renderUnavailableCross()}
        {this.props.children}
        {translate && <I18N id={text} defaultMessage={defaultText}/>}
        {!translate && text}
        {this.renderRunningAnimation()}
      </button>
    )
  }

  renderMenuArrow() {
    const { classes, menuArrow, menuOpened } = this.props
    const { pressed } = this.state

    if (!menuArrow) {
      return null
    }

    const menuDirectionClass = (menuOpened) ? classes.buttonMenuArrowDown : classes.buttonMenuArrowUp
    return (
      <i
        className={`${classes.buttonMenuArrow} ${menuDirectionClass}`}
        style={(pressed) ? this.arrowStylePressed : this.arrowStyle}
      />
    )
  }

  renderPopupArrow() {
    const { classes, menuArrow } = this.props
    const { pressed } = this.state

    if (!menuArrow) {
      return null
    }

    return <i className={classes.buttonPopupArrow} style={(pressed) ? this.arrowStylePressed : this.arrowStyle}/>
  }

  renderFeaturedRibbon() {
    const { classes, featuredRibbon } = this.props

    if (!featuredRibbon) {
      return null
    }

    return <i className={classes.buttonFeaturedRibbon}/>
  }

  renderUnavailableCross() {
    const { classes, unavailable } = this.props
    if (!unavailable) {
      return null
    }
    return <i className={classes.buttonUnavailableCross}/>
  }

  renderRunningAnimation() {
    const { classes } = this.props
    const { running } = this.state
    if (!running) {
      return null
    }
    return (
      <div className={classes.runningIcon}>
        <i className="fa fa-2x fa-spin fa-spinner"/>
      </div>
    )
  }
}

Button.propTypes = {
  msgBus: MessageBusPropTypes,
  classes: PropTypes.object,
  defaultActionBlocking: PropTypes.bool,
  onClick: PropTypes.func,
  doExecuteAction: PropTypes.func,
  executeActionProcessed: PropTypes.func,
  executeAction: PropTypes.oneOfType([PropTypes.func, PropTypes.array]),
  onActionFinish: PropTypes.func,
  actionRunning: PropTypes.object,
  dialogs: PropTypes.array,
  rounded: PropTypes.bool,
  menuArrow: PropTypes.bool,
  menuOpened: PropTypes.bool,
  featuredRibbon: PropTypes.bool,
  unavailable: PropTypes.bool,
  disabled: PropTypes.bool,
  style: PropTypes.object,
  stylePressed: PropTypes.object,
  styleDisabled: PropTypes.object,
  styleArrow: PropTypes.object,
  styleArrowPressed: PropTypes.object,
  className: PropTypes.string,
  classNamePressed: PropTypes.string,
  classNameDisabled: PropTypes.string,
  children: PropTypes.node,
  suppressLogging: PropTypes.bool,
  buttonElement: PropTypes.func,
  text: PropTypes.string,
  defaultText: PropTypes.string,
  blockOnActionRunning: PropTypes.bool
}

Button.defaultProps = {
  style: {},
  stylePressed: {},
  styleDisabled: {},
  styleArrow: {},
  styleArrowPressed: {},
  className: '',
  classNamePressed: '',
  classNameDisabled: '',
  suppressLogging: false,
  onActionFinish: null,
  blockOnActionRunning: null,
  defaultActionBlocking: false
}

function mapStateToProps({ actionRunning, theme, dialogs }) {
  const defaultActionBlocking = (theme || {}).defaultActionBlocking || false
  return {
    actionRunning,
    defaultActionBlocking,
    dialogs
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    doExecuteAction: executeAction,
    executeActionProcessed
  }, dispatch)
}

export default withExecuteActionMessageBus(connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(Button)))
