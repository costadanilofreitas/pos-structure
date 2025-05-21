import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { ensureArray } from '3s-posui/utils'

export default class Grid extends Component {
  render() {
    let { children, fluid } = this.props
    children = ensureArray(children)

    let fixedChildren = []
    children.forEach(child => {
      if (Array.isArray(child)) {
        fixedChildren = fixedChildren.concat(child)
      } else if (child.props != null) {
        fixedChildren.push(child)
      }
    })

    return (
      <div
        style={fluid ? { display: 'flex', flexDirection: 'column', height: '100%', width: '100%' } : {} }
        className={this.props.className}
      >
        {fixedChildren.map((row, index) =>
          (
            <div key={index} style={fluid ? { flex: '1' } : {} }>
              {React.cloneElement(row, { fluid: fluid })}
            </div>
          )
        )}
      </div>
    )
  }
}

Grid.propTypes = {
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  fluid: PropTypes.bool,
  className: PropTypes.string
}
