import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import injectSheet, { jss } from 'react-jss'
import { Button } from '../button'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  keyboardButtonRoot: {
    composes: 'keyboard-button-root',
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
    fontSize: '3vmin',
    height: '7vmin',
    textTransform: 'uppercase',
    width: '8vw',
    margin: '0.5vmin',
    backgroundColor: '#eeee',
    fontWeight: 300,
    '&:focus': {
      outline: 'none'
    },
    '&:disabled': {
      opacity: 0.4,
      cursor: 'default'
    },
    '&:active': {
      backgroundColor: '#cccccc'
    }
  }
}

class KeyboardButton extends PureComponent {
  handleClick = () => {
    this.props.onClick(this.props.value)
  }

  render() {
    const { classes, className, classNamePressed, rounded } = this.props
    return (
      <Button
        className={`${classes.keyboardButtonRoot} ${className}`}
        classNamePressed={classNamePressed}
        onClick={this.props.isDisabled ? null : this.handleClick}
        autoFocus={this.props.autofocus}
        disabled={this.props.isDisabled}
        rounded={rounded}
      >
        {this.props.value}
      </Button>
    )
  }
}

KeyboardButton.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  value: PropTypes.oneOfType([PropTypes.string.isRequired, PropTypes.node.isRequired]),
  className: PropTypes.string,
  classNamePressed: PropTypes.string,
  onClick: PropTypes.func.isRequired,
  autofocus: PropTypes.bool,
  isDisabled: PropTypes.bool,
  rounded: PropTypes.bool
}

KeyboardButton.defaultProps = {
  autofocus: false,
  isDisabled: false,
  className: '',
  rounded: false
}

export default injectSheet(styles)(KeyboardButton)
