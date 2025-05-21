import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { FormattedDate, FormattedTime } from 'react-intl'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  clockRoot: {
    composes: 'clock-root',
    boxSizing: 'border-box',
    MozBoxSizing: 'border-box',
    WebkitBoxSizing: 'border-box',
    position: 'absolute',
    top: '0px',
    right: '5px',
    height: '100%',
    color: theme.color || 'black',
    fontSize: '1.4vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    ...(theme.clock || {})
  }
})

/**
 * This component displays current date/time using default locale.
 * Notice that default styling if defined to be aligned to the right, since it usually used inside
 * the `InfoMessage` component, but you can override the styles or class as needed.
 *
 * Available class names:
 * - root element: `clock-root`
 */
class Clock extends PureComponent {
  constructor(props) {
    super(props)

    this.state = { dateTime: new Date() }
    this.updateDateTime = this.updateDateTime.bind(this)
    this.updateDateTimeInterval = null
  }

  render() {
    const { classes, style, showDate, showTime } = this.props
    const { dateTime } = this.state
    return (
      <span className={classes.clockRoot} style={style}>
        {showDate && <FormattedDate value={dateTime}/>}
        {showDate && showTime && <span>,&nbsp;</span>}
        {showTime && <FormattedTime value={dateTime}/>}
      </span>
    )
  }

  updateDateTime() {
    // only update the state if minutes have changed from the last update
    const newDateTime = new Date()
    const currentDateTime = this.state.dateTime
    if (newDateTime.toISOString().substr(0, 16) === currentDateTime.toISOString().substr(0, 16)) {
      return
    }
    this.setState({ dateTime: newDateTime })
  }

  componentDidMount() {
    this.updateDateTimeInterval = setInterval(() => (this.updateDateTime()), 500)
    this.updateDateTime()
  }

  componentWillUnmount() {
    if (this.updateDateTimeInterval) {
      clearInterval(this.updateDateTimeInterval)
    }
  }
}

Clock.propTypes = {
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
   * Show date
   */
  showDate: PropTypes.bool,
  /**
   * Show time
   */
  showTime: PropTypes.bool
}

Clock.defaultProps = {
  style: {},
  showDate: true,
  showTime: true
}

export default injectSheet(styles)(Clock)
