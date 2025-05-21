import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  contextMenuArrowCont: {
    composes: 'context-menu-arrow-cont',
    width: '100%',
    position: 'absolute',
    top: '100%',
    height: '1vh',
    justifyContent: 'center',
    display: 'flex',
    left: 0
  },
  contextMenuArrow: {
    composes: 'context-menu-arrow',
    fillRule: 'evenodd',
    strokeWidth: '2px',
    strokeLinecap: 'butt',
    strokeLinejoin: 'miter',
    strokeOpacity: 1,
    fillOpacity: 1,
    miterLimit: 0,
    fill: '#f2f2f2',
    stroke: '#999999'
  }
}

/**
 * A context menu helper that can be used as a container for a floating menu.
 * It draws a pointer on the bottom of the main container.
 * This component is used by ContextButton component.
 *
 * Available class names:
 * - main container element: `context-menu-arrow-cont`
 * - arrow element: `context-menu-arrow`
 */
class ContextMenu extends PureComponent {
  render() {
    const { classes } = this.props
    return (
      <div
        {..._.omit(this.props, ['classes', 'sheet', 'classNameArrowCont', 'classNameArrow', 'styleArrowCont', 'styleArrow', 'contextMenuElement'])}
        ref={(el) => (this.props.contextMenuElement(el))}
      >
        {this.props.children}
        <div
          className={`${classes.contextMenuArrowCont} ${this.props.classNameArrowCont}`}
          style={this.props.styleArrowCont}
        >
          <svg style={{ height: '100%', width: '3vh', display: 'block' }} viewBox="0 0 100 30" preserveAspectRatio="none">
            <path
              className={`${classes.contextMenuArrow} ${this.props.classNameArrow}`}
              style={this.props.styleArrow}
              d="M 0,0 50,30 100,0"
            />
          </svg>
        </div>
      </div>
    )
  }
}

ContextMenu.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Class name for context menu arrow container
   */
  classNameArrowCont: PropTypes.string,
  /**
   * Class name for context menu arrow
   */
  classNameArrow: PropTypes.string,
  /**
   * Override style for context menu arrow container
   */
  styleArrowCont: PropTypes.object,
  /**
   * Override style for context menu arrow
   */
  styleArrow: PropTypes.object,
  /**
   * Callback passing main context menu element
   */
  contextMenuElement: PropTypes.func,
  /**
   * The content of the context menu, it can be any valid react node
   */
  children: PropTypes.node
}

ContextMenu.defaultProps = {
  children: PropTypes.node,
  classNameArrowCont: '',
  classNameArrow: '',
  styleArrowCont: {},
  styleArrow: {},
  contextMenuElement: () => null
}

export default injectSheet(styles)(ContextMenu)
