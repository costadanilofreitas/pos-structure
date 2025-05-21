import React, { Component } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  screenSizeRoot: {
    composes: 'screen-size-root',
    position: 'absolute',
    right: 0,
    bottom: 0,
    padding: '5px',
    backgroundColor: 'white',
    opacity: 0.8
  }
}

/**
 * This utility widget displays the current screen size every time the window is resized
 *
 * Available class names:
 * - root element: `screen-size-root`
 */
class ScreenSize extends Component {
  constructor(props) {
    super(props)

    this.state = { width: 0, height: 0, delay: 3000, show: false }
    this.updateDimensions = this.updateDimensions.bind(this)
    this.hideDebounced = _.debounce(this.hideScreenSize, this.state.delay)
  }

  render() {
    const { classes, style } = this.props
    return (
      <span className={classes.screenSizeRoot} style={{ ...style, display: (this.state.show) ? 'initial' : 'none' }}>
        {this.state.width} x {this.state.height}
      </span>
    )
  }

  updateDimensions() {
    const w = window
    const d = document
    const documentElement = d.documentElement
    const body = d.getElementsByTagName('body')[0]
    const width = w.innerWidth || documentElement.clientWidth || body.clientWidth
    const height = w.innerHeight || documentElement.clientHeight || body.clientHeight

    this.setState({ width: width, height: height, show: true })
    this.hideDebounced()
  }

  componentDidMount() {
    window.addEventListener('resize', this.updateDimensions)
    this.updateDimensions()
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.updateDimensions)
    if (this.hideDebounced) {
      this.hideDebounced.cancel()
    }
  }

  hideScreenSize() {
    this.setState({ show: false })
  }
}

ScreenSize.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Component's root style override
   */
  style: PropTypes.object
}

ScreenSize.defaultProps = {
  style: {}
}

export default injectSheet(styles)(ScreenSize)
