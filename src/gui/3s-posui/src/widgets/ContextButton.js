import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import _ from 'lodash'
import injectSheet, { jss } from 'react-jss'
import memoize from 'memoize-one'
import { Button } from '../button'
import ContextMenu from './ContextMenu'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  contextButtonMenuCont: {
    composes: 'context-button-menu-cont',
    bottom: 'calc(100% + 1vh)',
    backgroundColor: '#f2f2f2',
    border: '1px solid #999',
    zIndex: '15'
  }
}

const events = ['mouseup', 'touchcancel']

/**
 * This component combines a button with a floating context menu.
 * Content children will be passed to the ContextMenu instance.
 * It handles clicks outside the component in order to close the context menu automatically.
 *
 * Available class names:
 * - main container element: `context-button-menu-cont`
 */
class ContextButton extends PureComponent {
  constructor(props) {
    super(props)
    this.button = null
    this.menu = null
    this.state = { show: false }
  }

  genStylesMemo = (
    show, numChildren, autoHeight, styleContextMenu, styleArrowCont, styleArrow
  ) => {
    const top = (numChildren) ? `calc(-${100 * numChildren}% - 1vh)` : 'auto'
    const autoHeightStyle = (autoHeight) ? { top, height: '100%' } : {}
    this.contextMenuStyle = {
      position: 'absolute',
      display: (show) ? 'inline' : 'none',
      ...autoHeightStyle,
      ...styleContextMenu
    }
    if (autoHeight) {
      this.styleArrowCont = {
        top: `${100 * numChildren}%`,
        ...styleArrowCont
      }
      this.styleArrow = {
        top: 0,
        ...styleArrow
      }
    } else {
      this.styleArrowCont = styleArrowCont
      this.styleArrow = styleArrow
    }
  }

  genStyles = memoize(this.genStylesMemo)

  closeContextMenu = () => {
    this.setState({ show: false })
  }

  componentDidMount() {
    _.forEach(events, (e) => {
      document.addEventListener(e, this.handleClickOutside, true)
    })
  }

  componentWillUnmount() {
    _.forEach(events, (e) => {
      document.removeEventListener(e, this.handleClickOutside, true)
    })
  }

  contextMenuElement = (el) => {
    this.menu = el
  }

  handleClickOutside = (e) => {
    if (this.menu && this.state.show) {
      if (this.button && this.button.contains(e.target)) {
        return
      }
      this.closeContextMenu()
    }
  }

  handleButtonRef = (el) => {
    this.button = el
  }

  render() {
    const {
      classes, children, className, style, classNameContextMenu, styleContextMenu,
      classNameArrowCont, classNameArrow, styleArrowCont, styleArrow, classNameButton,
      classNameButtonPressed, styleButton, styleButtonPressed, buttonText, styleButtonArrow,
      styleButtonArrowPressed, autoHeight
    } = this.props
    const { show } = this.state

    const childrenWithProps = React.Children.map(children || [], (child) => {
      if (!child) {
        return null
      }
      return React.cloneElement(child, { closeContextMenu: this.closeContextMenu })
    })

    this.genStyles(
      show, childrenWithProps.length, autoHeight, styleContextMenu, styleArrowCont, styleArrow
    )
    return (
      <div className={className} style={style}>
        <ContextMenu
          contextMenuElement={this.contextMenuElement}
          className={`${classes.contextButtonMenuCont} ${classNameContextMenu}`}
          style={this.contextMenuStyle}
          classNameArrowCont={classNameArrowCont}
          classNameArrow={classNameArrow}
          styleArrowCont={this.styleArrowCont}
          styleArrow={this.styleArrow}
        >
          {childrenWithProps}
        </ContextMenu>
        <Button
          buttonElement={this.handleButtonRef}
          className={classNameButton}
          classNamePressed={classNameButtonPressed}
          menuArrow={true}
          menuOpened={show}
          style={styleButton}
          stylePressed={styleButtonPressed}
          styleArrow={styleButtonArrow}
          styleArrowPressed={styleButtonArrowPressed}
          onClick={() => (this.setState({ show: !show }))}
        >
          {buttonText}
        </Button>
      </div>
    )
  }
}

ContextButton.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Calculate context menu height automatically based on the number of children items, assuming
   * they will have the same size as the main button
   */
  autoHeight: PropTypes.bool,
  /**
   * Text to display on the button
   */
  buttonText: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  /**
   * Class name for container
   */
  className: PropTypes.string,
  /**
   * Class name for button
   */
  classNameButton: PropTypes.string,
  /**
   * Class name for button when pressed
   */
  classNameButtonPressed: PropTypes.string,
  /**
   * Class name for context menu
   */
  classNameContextMenu: PropTypes.string,
  /**
   * Class name for context menu arrow container
   */
  classNameArrowCont: PropTypes.string,
  /**
   * Class name for context menu arrow
   */
  classNameArrow: PropTypes.string,
  /**
   * Override style for main container
   */
  style: PropTypes.object,
  /**
   * Override style for the button
   */
  styleButton: PropTypes.object,
  /**
   * Override style for the button when pressed
   */
  styleButtonPressed: PropTypes.object,
  /**
   * Override style for context menu
   */
  styleContextMenu: PropTypes.object,
  /**
   * Override style for context menu arrow container
   */
  styleArrowCont: PropTypes.object,
  /**
   * Override style for context menu arrow
   */
  styleArrow: PropTypes.object,
  /**
   * A custom style for the button arrow
   */
  styleButtonArrow: PropTypes.object,
  /**
   * A custom style for the button arrow when pressed
   */
  styleButtonArrowPressed: PropTypes.object,
  /**
   * The content of the context menu, it can be any valid react node
   */
  children: PropTypes.node
}

ContextButton.defaultProps = {
  autoHeight: false,
  buttonText: '',
  style: {},
  styleButton: {},
  styleButtonPressed: {},
  styleContextMenu: {},
  styleArrowCont: {},
  styleArrow: {},
  className: '',
  classNameButton: '',
  classNameButtonPressed: '',
  classNameContextMenu: '',
  classNameArrowCont: '',
  classNameArrow: ''
}

export default injectSheet(styles)(ContextButton)
