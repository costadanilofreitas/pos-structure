import React, { Component } from 'react'
import PropTypes from 'prop-types'

export default class PopMenu extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { containerClassName, menuVisible, controllerRef, menuStyle, menuClassName } = this.props

    if (!menuVisible || controllerRef == null) {
      return this.props.children[0]
    }

    let actualStyle = {
      position: 'fixed',
      zIndex: '2'
    }

    if (this.props.position === 'above') {
      actualStyle.bottom = window.innerHeight - controllerRef.getBoundingClientRect().top
    } else {
      actualStyle.top = controllerRef.getBoundingClientRect().bottom
    }
    actualStyle.width = controllerRef.getBoundingClientRect().width

    if (this.props.menuStyle != null) {
      actualStyle = Object.assign(actualStyle, menuStyle)
    }

    return (
      <div className={containerClassName}>
        {this.props.children[0]}
        <div style={actualStyle} className={menuClassName}>
          {this.props.children[1]}
        </div>
      </div>
    )
  }
}

PopMenu.propTypes = {
  position: PropTypes.oneOf(['above', 'below']),
  containerClassName: PropTypes.string,
  menuStyle: PropTypes.object,
  menuClassName: PropTypes.string,
  menuVisible: PropTypes.bool,
  controllerRef: PropTypes.object,
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object])
}
