/* eslint-disable no-bitwise */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import injectSheet, { jss } from 'react-jss'
import { parseISO8601Date } from '../utils'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  kdsCellTimerRoot: {
    composes: 'kds-cell-timer-root'
  }
}

class KDSCellTimer extends Component {
  constructor(props) {
    super(props)
    const { secs, mins, hour } = KDSCellTimer.formatTime(props.startTime, props.isGMT, props.backwards, props.timeDelta)

    this.state = {
      secs,
      mins,
      hour,
      timer: props.globalTimer,
      startTime: props.startTime,
      backwards: props.backwards
    }
  }

  fastPad(pad, str, padLeft) {
    if (typeof str === 'undefined') {
      return pad
    }
    if (padLeft) {
      return (pad + str).slice(-pad.length)
    }

    return (str + pad).substring(0, pad.length)
  }

  static formatTime(timestamp, isGMT, backwards, timeDelta) {
    if (!timestamp) {
      return { hour: '', mins: '', secs: '' }
    }
    let date = timestamp
    if (!(date instanceof Date)) {
      date = parseISO8601Date(timestamp, isGMT)
    }
    let timeDiff
    if (backwards === true) {
      timeDiff = (date - new Date()) - timeDelta
    } else {
      timeDiff = (new Date() - date) + timeDelta
    }

    const hour = ~~(timeDiff / 3600000)
    const mins = ~~((timeDiff / 60000) % 60)
    const secs = ~~((timeDiff / 1000) % 60)

    return { hour, mins, secs }
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const { startTime, isGMT, backwards, timeDelta, globalTimer } = nextProps
    let secs
    let mins
    let hour

    if (prevState.startTime !== startTime || prevState.backwards !== backwards) {
      ({ secs, mins, hour } = KDSCellTimer.formatTime(startTime, isGMT, backwards, timeDelta))

      return {
        secs: secs % 60,
        mins: mins % 60,
        hour: hour,
        timer: globalTimer,
        startTime: startTime,
        backwards: backwards
      }
    }

    const diff = nextProps.globalTimer - prevState.timer
    if (diff < nextProps.interval) {
      return prevState
    }

    if (nextProps.backwards !== true) {
      secs = prevState.secs + (diff % 60)
      mins = prevState.mins + (~~(secs / 60) % 60) + (~~(diff / 60) % 60)
      hour = prevState.hour + ~~(mins / 60) + ~~(diff / 3600)
    } else {
      secs = (prevState.secs + 60) - (diff % 60)
      mins = (prevState.mins + 60) - (1 - ~~(secs / 60)) - (~~(diff / 60) % 60)
      hour = prevState.hour - (1 - ~~(mins / 60)) - ~~(diff / 3600)
    }

    return {
      secs: secs % 60,
      mins: mins % 60,
      hour: hour,
      timer: nextProps.globalTimer,
      startTime: nextProps.startTime
    }
  }

  shouldComponentUpdate(nextProps, nextState) {
    return nextState !== this.state
  }

  render() {
    const { classes, style } = this.props
    const { hour, mins, secs, backwards } = this.state
    const minSecs = `${this.fastPad('00', mins, true)}:${this.fastPad('00', secs, true)}`

    const currTime = (hour > 0) ? `${this.fastPad('00', hour, true)}:${minSecs}` : minSecs
    return (
      <span className={classes.kdsCellTimerRoot} style={style}>
        {backwards !== true ? currTime : `-${currTime}`}
      </span>
    )
  }
}

KDSCellTimer.propTypes = {
  classes: PropTypes.object,
  style: PropTypes.object,
  startTime: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
  backwards: PropTypes.bool,
  isGMT: PropTypes.bool,
  globalTimer: PropTypes.number,
  interval: PropTypes.number,
  timeDelta: PropTypes.number
}

KDSCellTimer.defaultProps = {
  style: {},
  interval: 1
}

function mapStateToProps({ globalTimer, timeDelta }) {
  return {
    globalTimer,
    timeDelta
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(KDSCellTimer))
