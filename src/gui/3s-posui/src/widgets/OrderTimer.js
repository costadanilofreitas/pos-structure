import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  orderTimerRoot: {
    composes: 'order-timer-root'
  }
}

/**
 * Display the order time since the order was created.
 *
 * In order to use this component, your app state must expose the following states:
 * - `timeDelta` using `timeDeltaReducer` reducer
 *
 * Available class names:
 * - root element: `order-timer-root`
 */
class OrderTimer extends PureComponent {
  state = {
    time: null
  }

  formatTime = (timestamp) => {
    const { timeDelta } = this.props
    // notice that (new Date()).getTime() is not consistent accross browsers / guicomp2,
    // some versions returns with the TZ offset, other versions not.
    const now = new Date()
    // eslint-disable-next-line prefer-template
    const iso = now.getFullYear() + '-' +
                _.padStart(now.getMonth() + 1, 2, '0') + '-' +
                _.padStart(now.getDate(), 2, '0') + 'T' +
                _.padStart(now.getHours(), 2, '0') + ':' +
                _.padStart(now.getMinutes(), 2, '0') + ':' +
                _.padStart(now.getSeconds(), 2, '0') + '.000'
    const ellapsed = (new Date(iso)).getTime() - (new Date(timestamp)).getTime()
    const timeDiff = new Date(ellapsed + timeDelta)
    if (timeDiff < 0) {
      return null
    }
    const hours = parseInt(timeDiff / 3600000, 10)
    const mins = _.padStart(parseInt(timeDiff / 60000, 10) % 60, 2, '0')
    const secs = _.padStart(parseInt(timeDiff / 1000, 10) % 60, 2, '0')
    const minSec = `${mins}:${secs}`
    if (hours > 0) {
      if (hours > 24) {
        const days = parseInt(hours / 24, 10)
        return `${days} ${_.padStart(hours % 24, 2, '0')}:${minSec}`
      }
      return `${_.padStart(hours, 2, '0')}:${minSec}`
    }
    return minSec
  }

  componentDidMount() {
    this.interval = setInterval(() => this.setState({ time: Date.now() }), 1000)
  }

  componentWillUnmount() {
    clearInterval(this.interval)
  }

  updateDisplayTime = () => {
    const { order } = this.props
    const time = (order['@attributes'] || {}).createdAt
    if (!time) {
      return
    }
    const displayTime = this.formatTime(time)
    if (this.displayTime !== displayTime) {
      this.displayTime = displayTime
    }
  }

  render() {
    const { classes, style } = this.props
    this.updateDisplayTime()

    return (
      <span className={classes.orderTimerRoot} style={style}>
        {this.displayTime}
      </span>
    )
  }
}

OrderTimer.propTypes = {
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
   * Time difference between the server and current box (in ms.)
   * This property comes from timeDeltaReducer
   */
  timeDelta: PropTypes.number,
  /**
   * Order object
   */
  order: PropTypes.object.isRequired
}

OrderTimer.defaultProps = {
  style: {},
  timeDelta: 0,
  order: {}
}

function mapStateToProps({ timeDelta }) {
  return {
    timeDelta
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(OrderTimer))
