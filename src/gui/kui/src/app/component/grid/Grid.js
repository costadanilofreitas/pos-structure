import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { ensureArray } from '3s-posui/utils'

const fluidStyle = { flex: '1' }

export default class Grid extends Component {
  constructor(props) {
    super(props)

    this.handleReference = this.handleReference.bind(this)
  }

  render() {
    let { children, fluid, fontSizeZoom } = this.props
    children = ensureArray(children)

    let fixedChildren = []
    children.forEach(child => {
      if (Array.isArray(child)) {
        fixedChildren = fixedChildren.concat(child)
      } else if (child.props !== undefined) {
        fixedChildren.push(child)
      }
    })

    return (
      <div
        style={fluid
          ? { display: 'flex', flexDirection: 'column', height: '100%', width: '100%', fontSize: `${fontSizeZoom}vh` }
          : { fontSize: `${fontSizeZoom}vh` }
        }
        className={this.props.className}
        ref={this.handleReference}
      >
        {fixedChildren.map((row, index) => {
          return (
            <div key={index} style={fluid ? fluidStyle : null}>
              {React.cloneElement(row, { fluid: fluid })}
            </div>
          )
        }
        )}
      </div>
    )
  }

  handleReference(ref) {
    if (this.props.reference != null) {
      this.props.reference(ref)
    }
  }
}

Grid.propTypes = {
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  fluid: PropTypes.bool,
  className: PropTypes.string,
  reference: PropTypes.func,
  fontSizeZoom: PropTypes.number
}
