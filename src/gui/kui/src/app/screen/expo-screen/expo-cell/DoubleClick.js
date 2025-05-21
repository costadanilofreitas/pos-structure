import React, { Component } from 'react'
import PropTypes from 'prop-types'

export default class DoubleClick extends Component {
  constructor(props) {
    super(props)
    this.onClick = this.onClick.bind(this)
    this.onDoubleClick = this.onDoubleClick.bind(this)
    this.timeout = null
  }
  timeoutHandler = () => {
    this.timeout = null
    this.props.onClick()
  }
  onClick(e) {
    e.preventDefault()

    if (this.timeout === null) {
      this.timeout = setTimeout(this.timeoutHandler, 300)
    }
  }

  onDoubleClick(e) {
    e.preventDefault()
    clearTimeout(this.timeout)
    this.timeout = null
    this.props.onDoubleClick()
  }

  render() {
    const { children, ...childProps } = this.props
    const props = Object.assign(childProps, { onClick: this.onClick, onDoubleClick: this.onDoubleClick })
    return React.cloneElement(children, props)
  }
}

DoubleClick.propTypes = {
  onClick: PropTypes.func.isRequired,
  onDoubleClick: PropTypes.func.isRequired,
  children: PropTypes.element.isRequired
}
