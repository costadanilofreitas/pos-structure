import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import injectSheet, { jss } from 'react-jss'
import { I18N } from '../core'
import { dismissInfoMessageAction } from '../actions'
import Clock from './Clock'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  infoMessageRoot: {
    composes: 'info-message-root',
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center'
  },
  infoMessageIcon: {
    composes: 'fa info-message-icon',
    padding: '0 5px'
  },
  infoMessageInfo: {
    composes: 'info-message-info',
    backgroundColor: '#d9ecec'
  },
  infoMessageInfoIcon: {
    composes: 'fa-comment info-message-info-icon',
    color: '#81c0c0'
  },
  infoMessageSuccess: {
    composes: 'info-message-success',
    backgroundColor: '#e1e7cd'
  },
  infoMessageSuccessIcon: {
    composes: 'fa-check info-message-success-icon',
    color: '#588c75'
  },
  infoMessageError: {
    composes: 'info-message-error',
    backgroundColor: '#f1c1bd'
  },
  infoMessageErrorIcon: {
    composes: 'fa-times info-message-error-icon',
    color: '#da645a'
  },
  infoMessageWarning: {
    composes: 'info-message-warning',
    backgroundColor: '#faf4d4'
  },
  infoMessageWarningIcon: {
    composes: 'fa-exclamation info-message-warning-icon',
    color: '#cabd7c'
  },
  infoMessageCritical: {
    composes: 'info-message-critical',
    backgroundColor: '#f1c1bd'
  },
  infoMessageCriticalIcon: {
    composes: 'fa-exclamation-triangle info-message-critical-icon',
    color: '#da645a'
  }
}

/**
 * Displays information messages comming from MW:APP POS controller.
 *
 * In order to use this component, your app state must expose the following states:
 * - `infoMessage` using `infoMessageReducer` reducer
 *
 * Available class names:
 * - root element: `info-message-root`
 * - icon element: `info-message-icon`
 * - icon info: `info-message-info-icon`
 * - icon success: `info-message-success-icon`
 * - icon error: `info-message-error-icon`
 * - icon warning: `info-message-warning-icon`
 * - icon critical: `info-message-critical-icon`
 * - root info: `info-message-info`
 * - root success: `info-message-success`
 * - root error: `info-message-error`
 * - root warning: `info-message-warning`
 * - root critical: `info-message-critical`
 */
class InfoMessage extends PureComponent {
  constructor(props) {
    super(props)

    this.timer = null
    this.hideInfoMessage = this.hideInfoMessage.bind(this)
    this.state = { show: false }
  }

  componentDidUpdate() {
    let timer = this.timer
    if (timer) {
      // clear any setTimeout in progress
      clearTimeout(timer)
      timer = null
    }
    if (this.props.infoMessage) {
      const timeout = parseInt(this.props.infoMessage.timeout, 10)
      // note that -1 or NaN timeouts will result in not clearing the message
      if (!isNaN(timeout) && timeout >= 0) {
        timer = setTimeout(this.hideInfoMessage, timeout)
      }
    } else {
      this.hideInfoMessage()
    }
    this.timer = timer
  }

  hideInfoMessage() {
    this.timer = null
    this.props.dismissInfoMessage()
  }

  getRootClass = (type) => {
    const { classes } = this.props
    const rootClassMap = {
      info: classes.infoMessageInfo,
      success: classes.infoMessageSuccess,
      error: classes.infoMessageError,
      warning: classes.infoMessageWarning,
      critical: classes.infoMessageCritical
    }
    const rootClass = rootClassMap[type] || `info-message-${type}`
    return `${classes.infoMessageRoot} ${rootClass}`
  }

  getIconClass = (type) => {
    const { classes } = this.props
    const iconClassMap = {
      info: classes.infoMessageInfoIcon,
      success: classes.infoMessageSuccessIcon,
      error: classes.infoMessageErrorIcon,
      warning: classes.infoMessageWarningIcon,
      critical: classes.infoMessageCriticalIcon
    }
    const iconClass = iconClassMap[type] || `info-message-${type}-icon`
    return `${classes.infoMessageIcon} ${iconClass}`
  }

  render() {
    const { style, showClock } = this.props
    const infoMessage = this.props.infoMessage || {}
    const type = infoMessage.type
    return (
      <div className={this.getRootClass(type)} style={style}>
        {type && <i className={this.getIconClass(type)}></i>}
        <I18N id={infoMessage.msg} noLineBreak={true} />
        {showClock && <Clock />}
      </div>
    )
  }
}

InfoMessage.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Component's root style override
   */
  style: PropTypes.object,
  /**
   * Info message data
   * @ignore
   */
  infoMessage: PropTypes.object,
  /**
   * Info message dismiss action
   * @ignore
   */
  dismissInfoMessage: PropTypes.func,
  /**
   * Display clock with current date/time
   */
  showClock: PropTypes.bool
}

InfoMessage.defaultProps = {
  style: {},
  showClock: true
}

function mapStateToProps(state) {
  return {
    infoMessage: state.infoMessage
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({ dismissInfoMessage: dismissInfoMessageAction }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(InfoMessage))
