import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import shallowEqual from 'react-redux/lib/utils/shallowEqual'
import Color from 'color'
import injectSheet, { jss } from 'react-jss'
import memoize from 'memoize-one'
import { I18N } from '../core'
import { executeAction, executeActionProcessed, buttonDownAction, buttonUpAction } from '../actions'
import { ENABLE_USABILITY_LOG } from '../constants/config'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  buttonRoot: {
    composes: 'button-root',
    border: 'none',
    fontSize: '1.6vh',
    outline: 'none',
    position: 'relative',
    height: '100%',
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  buttonRounded: {
    composes: 'button-rounded',
    borderRadius: '5px'
  },
  buttonFeatured: {
    composes: 'button-featured',
    border: '2px solid rgba(0, 0, 0, 0.5)',
    overflow: 'hidden'
  },
  buttonFeaturedRibbon: {
    composes: 'button-featured-ribbon fa fa-minus fa-2x',
    position: 'absolute',
    width: '10%',
    height: '10%',
    right: '-3%',
    top: '-11%',
    transform: 'rotate(45deg)',
    color: 'rgba(0, 0, 0, 0.5)'
  },
  buttonUnavailable: {
    composes: 'button-unavailable',
    backgroundColor: '#dddddd',
    color: '#878787',
    border: '1px solid #C1C1C1'
  },
  buttonUnavailableCross: {
    composes: 'button-unavailable-cross fa fa-times fa-5x',
    position: 'absolute',
    color: 'rgba(255, 255, 255, 0.5)'
  },
  buttonDisabled: {
    composes: 'button-disabled',
    backgroundColor: '#dddddd',
    color: '#878787'
  },
  buttonMenuArrow: {
    composes: 'button-menu-arrow fa',
    position: 'absolute',
    width: '100%',
    left: 0,
    top: '2%'
  },
  buttonMenuArrowUp: {
    composes: 'button-menu-arrow-up fa-chevron-up'
  },
  buttonMenuArrowDown: {
    composes: 'button-menu-arrow-down fa-chevron-down'
  },
  buttonPopupArrow: {
    composes: 'button-popup-arrow fa fa-sort-up fa-2x',
    position: 'absolute',
    top: '0',
    width: '2vh',
    right: '0',
    height: '2vh',
    transform: 'rotate(45deg)',
    msTransform: 'rotate(45deg)',
    WebkitTransform: 'rotate(45deg)'
  }
}

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
    this.state = {
      pressed: true // initialize as pressed, so we can force a redraw on component mount
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
    classNamePressed, classNameDisabled, classes, rounded, featuredRibbon, unavailable, disabled
  ) => {
    if (!button) {
      return
    }
    // generate classes
    const buttonClass = (disabled) ? [classes.buttonRoot] : [classes.buttonRoot, className]
    if (rounded) {
      buttonClass.push(classes.buttonRounded)
    }
    if (featuredRibbon) {
      buttonClass.push(classes.buttonFeatured)
    }
    if (unavailable) {
      buttonClass.push(classes.buttonUnavailable)
    }
    if (disabled) {
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
    // foreground color
    let color = 'black'
    if (this.props.children || this.props.text) {
      color = computedStyle.color
      // since "ButtonText" is not a color, let's put a default color here
      if (color === 'ButtonText') {
        color = 'black'
      }
      if (this.colorEquals(color, 'black')) {
        color = this.chooseContrastColor(backgroundColor)
      }
    }
    if (!disabled) {
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
    return (newColor1.rgb().string()) === (newColor2.rgb().string())
  }

  mouseEnter = (evt) => {
    const { actionRunning } = this.props
    // block when an action is running
    if (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning)) {
      return
    }
    // check if button is pressed
    if (evt.buttons === 1 && !this.props.disabled) {
      this.setPressed()
    }
    evt.stopPropagation()
    evt.preventDefault()
  }

  mouseLeave = (evt, nativeEvt, clicked) => {
    const { pressed } = this.state
    const { actionRunning } = this.props
    // block when an action is running
    if (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning)) {
      return
    }
    if (pressed) {
      if (ENABLE_USABILITY_LOG) {
        // this action is used for logging and usability study
        this.props.buttonUpAction(this.text, clicked || false)
      }
      this.setState({ pressed: false })
    }
    if (evt && evt.stopPropagation) {
      evt.stopPropagation()
      evt.preventDefault()
    }
  }

  mouseDown = (evt) => {
    const { actionRunning } = this.props
    // block when an action is running
    if (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning)) {
      return
    }
    if (!this.props.disabled) {
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
    if (this.actionBlocking && this.props.executeAction && !_.isEmpty(actionRunning)) {
      return
    }
    if (this.props.onClick) {
      this.props.onClick()
    } else if (this.props.executeAction) {
      let params = null
      if (typeof (this.props.executeAction) === 'function') {
        params = this.props.executeAction()
      } else {
        params = this.props.executeAction
      }
      if (params && params.length) {
        let localActionId = null
        if (this.props.onActionFinish) {
          // we need to track the response
          localActionId = _.uniqueId('action_')
          this.localActionId.push(localActionId)
        }
        this.props.doExecuteAction(localActionId, ...params)
        if (ENABLE_USABILITY_LOG) {
          this.props.buttonUpAction(this.text, true)
        }
        return
      }
    }
    this.mouseLeave(evt, null, true)
  }

  setPressed() {
    const { pressed } = this.state
    if (!pressed) {
      if (ENABLE_USABILITY_LOG) {
        // this action is used for logging and usability study
        this.props.buttonDownAction(this.text)
      }
      this.setState({ pressed: true })
    }
  }

  chooseContrastColor = (color) => {
    return ((new Color(color)).luminosity() > 0.179) ? '#000000' : '#FFFFFF'
  }

  componentDidUpdate(prevProps) {
    if ((this.props.blockOnActionRunning !== prevProps.blockOnActionRunning) ||
        (this.props.defaultActionBlocking !== prevProps.defaultActionBlocking)) {
      this.setActionBlocking(this.props)
    }
    if (this.props.actionRunning === prevProps.actionRunning) {
      return
    }
    // check if asynchronous action is finished and we need to fire executeActionProcessed
    const hasActions = !_.isEmpty(this.props.actionRunning)
    if (hasActions && this.localActionId.length > 0) {
      const matchedActions = _.intersection(_.keys(this.props.actionRunning), this.localActionId)
      if (matchedActions.length > 0) {
        _.forEach(matchedActions, (localActionId) => {
          const actionData = this.props.actionRunning[localActionId]
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
    if (pressed && (!this.props.executeAction || !hasActions)) {
      this.setState({ pressed: false })
    }
  }

  shouldComponentUpdate(nextProps, nextState) {
    const eqProps = shallowEqual(this.props, nextProps)
    const eqState = shallowEqual(this.state, nextState)
    const shouldUpdate = !(eqProps && eqState)
    if (shouldUpdate && eqState) {
      // We can safely ignore the following properties from updating the UI, as they don't affect
      // the visual output. They might appear different on every render if the user passes an
      // inline function.
      //
      // So, the following pattern should be AVOIDED:
      //   <Button onClick={() => { ... }} ... />
      //
      // instead, use an instance function:
      //   <Button onClick={this.handleOnClick} ... />
      //
      const ignoreProps = ['actionRunning', 'onClick', 'executeAction', 'onActionFinish']
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
    const {
      style, stylePressed, styleDisabled, className, classNamePressed, classNameDisabled,
      styleArrow, styleArrowPressed, classes, rounded, featuredRibbon, unavailable, disabled
    } = this.props
    this.genStyles(
      this.button, style, stylePressed, styleDisabled, styleArrow, styleArrowPressed, className,
      classNamePressed, classNameDisabled, classes, rounded, featuredRibbon, unavailable, disabled
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
  }

  render() {
    const { pressed } = this.state
    const {
      style, stylePressed, styleDisabled, styleArrow, styleArrowPressed, className,
      classNamePressed, classNameDisabled, classes, rounded, featuredRibbon, unavailable, disabled,
      text, defaultText
    } = this.props
    this.genStyles(
      this.button, style, stylePressed, styleDisabled, styleArrow, styleArrowPressed, className,
      classNamePressed, classNameDisabled, classes, rounded, featuredRibbon,
      unavailable, disabled
    )
    const translate = text && _.startsWith(text, '$')
    const menuArrowDirection = (this.props.menuOpened) ? classes.buttonMenuArrowDown : classes.buttonMenuArrowUp
    return (
      <button
        ref={this.buttonRef}
        className={(pressed) ? this.buttonClassPressed : this.buttonClass}
        disabled={disabled}
        onMouseEnter={this.mouseEnter}
        onMouseLeave={this.mouseLeave}
        onMouseUp={this.mouseUp}
        onMouseDown={this.mouseDown}
        style={(pressed) ? this.buttonStylePressed : this.buttonStyle}
      >
        {this.props.menuArrow &&
          <i
            className={`${classes.buttonMenuArrow} ${menuArrowDirection}`}
            style={(pressed) ? this.arrowStylePressed : this.arrowStyle}
          />
        }
        {this.props.popupArrow &&
          <i
            className={classes.buttonPopupArrow}
            style={(pressed) ? this.arrowStylePressed : this.arrowStyle}
          />
        }
        {this.props.featuredRibbon &&
        <i className={classes.buttonFeaturedRibbon} />}
        {this.props.unavailable &&
        <i className={classes.buttonUnavailableCross} />}
        {this.props.children}
        {translate && <I18N id={text} defaultMessage={defaultText} />}
        {!translate && text}
      </button>
    )
  }
}

Button.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Block clicks when an action is running
   * @ignore
   */
  defaultActionBlocking: PropTypes.bool,
  /**
   * A function to be called when the user clicks the button
   */
  onClick: PropTypes.func,
  /**
   * Action creator to run an MW action on the server via executeSaga
   * @ignore
   */
  doExecuteAction: PropTypes.func,
  /**
   * Action creator to set an action as processed (remove from actionRunning state)
   * @ignore
   */
  executeActionProcessed: PropTypes.func,
  /**
   * Action creator to log when a button is pressed for usage usability studies
   * @ignore
   */
  buttonDownAction: PropTypes.func,
  /**
   * Action creator to log when a button is released for usage usability studies
   * @ignore
   */
  buttonUpAction: PropTypes.func,
  /**
   * Executes an MW action on the server. If an array is specified, the first element is the name
   * of the action and the following the parameters. If a function is specified, it must return an
   * array in the same format.
   */
  executeAction: PropTypes.oneOfType([PropTypes.func, PropTypes.array]),
  /**
   * Optional callback to be called when the action finishes
   */
  onActionFinish: PropTypes.func,
  /**
   * App state holding actions currently in progress
   * @ignore
   */
  actionRunning: PropTypes.object,
  /**
   * Use rounded corners on the button
   */
  rounded: PropTypes.bool,
  /**
   * Display a menu arrow on the top-middle of the button, to indicate that this button opens
   * a menu. The arrow will be pointing up or down according to the `menuOpened` property.
   */
  menuArrow: PropTypes.bool,
  /**
   * Used to determine if the menu array must be pointing up or down.
   */
  menuOpened: PropTypes.bool,
  /**
   * Displays an arrow on the top-right corner of the button to indicate that this button opens
   * a pop-up window
   */
  popupArrow: PropTypes.bool,
  /**
   * Displays a ribbon on the corner of the button to remark a featured product
   */
  featuredRibbon: PropTypes.bool,
  /**
   * Displays a cross on the button. Used to indicate that a product is not available for sale.
   */
  unavailable: PropTypes.bool,
  /**
   * Disable the button
   */
  disabled: PropTypes.bool,
  /**
   * A custom style for the button
   */
  style: PropTypes.object,
  /**
   * A custom style for the button when pressed
   */
  stylePressed: PropTypes.object,
  /**
   * A custom style for the button when disabled
   */
  styleDisabled: PropTypes.object,
  /**
   * A custom style for the arrow
   */
  styleArrow: PropTypes.object,
  /**
   * A custom style for the arrow when pressed
   */
  styleArrowPressed: PropTypes.object,
  /**
   * A custom class name to append to the button
   */
  className: PropTypes.string,
  /**
   * A custom class name to append to the button when it is pressed
   */
  classNamePressed: PropTypes.string,
  /**
   * A custom class name to append to the button when it is disabled
   */
  classNameDisabled: PropTypes.string,
  /**
   * Children elements
   * @ignore
   */
  children: PropTypes.node,
  /**
   * Do not log button text as it might contain sensitive information (e.g. password numpad)
   */
  suppressLogging: PropTypes.bool,
  /**
   * When the button is instantiated, this function will be called passin a reference to the main
   * element as parameter
   */
  buttonElement: PropTypes.func,
  /**
   * Button text. If the text starts with $ it will be automatically translated, this is the
   * preferred way, instead of passing an <I18N/> instance, to avoid unnecessary renders
   */
  text: PropTypes.string,
  /**
   * Default text in case that text translation is missing
   */
  defaultText: PropTypes.string,
  /**
   * Block clicks when an action is running
   */
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
  buttonDownAction: () => null,
  buttonUpAction: () => null,
  onActionFinish: null,
  blockOnActionRunning: null,
  defaultActionBlocking: false
}

function mapStateToProps({ actionRunning, theme }) {
  const defaultActionBlocking = (theme || {}).defaultActionBlocking || false
  return {
    actionRunning,
    defaultActionBlocking
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    doExecuteAction: executeAction,
    executeActionProcessed,
    buttonDownAction,
    buttonUpAction
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(Button))
