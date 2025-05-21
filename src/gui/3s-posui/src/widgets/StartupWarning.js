import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  styleStartupWarning: {
    composes: 'startup-warning-root',
    color: '#777777',
    position: 'fixed',
    textAlign: 'center',
    width: '100%',
    top: '30px'
  },
  styleStartupWarningIcon: {
    composes: 'fa fa-warning fa-2x startup-warning-icon',
    paddingRight: '10px',
    verticalAlign: 'middle'
  }
}

/**
 * This component is used by `LoadingScreen` to display an error message along with a warning icon.
 *
 * Available class names:
 * - root element: `startup-warning-root`
 * - spinner element: `startup-warning-icon`
 */
class StartupWarning extends PureComponent {
  render() {
    const { classes, style, styleIcon } = this.props
    return (
      <div className={classes.styleStartupWarning} style={style}>
        <div className={classes.styleStartupWarningIcon} style={styleIcon}/>
        {this.props.msg}
      </div>
    )
  }
}

StartupWarning.propTypes = {
  /**
   * The message to be displayed
   */
  msg: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
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
   * Component's icon style override
   */
  styleIcon: PropTypes.object
}

StartupWarning.defaultProps = {
  style: {},
  styleIcon: {}
}

export default injectSheet(styles)(StartupWarning)
