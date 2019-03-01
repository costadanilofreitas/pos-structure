import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { showInfoMessageAction } from 'posui/actions'
import { Button } from 'posui/button'
import injectSheet, { jss } from 'react-jss'
import { MENU_PAYMENT, MENU_ORDER, MENU_MANAGER } from '../reducers/menuReducer'
import setMenuAction from '../actions/setMenuAction'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  menuContainer: {
    composes: 'menu-container',
    display: 'flex',
    width: '100%',
    height: '100%',
    backgroundColor: 'black',
    position: 'absolute'
  },
  menuButton: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '1px'
  },
  menu: {
    backgroundColor: 'white',
    color: 'black',
    fontSize: '2vh',
    textTransform: 'none',
    ...(theme.mainMenu || {})
  },
  menuActive: {
    backgroundColor: 'black',
    color: 'white',
    ...(theme.mainMenuActive || {})
  },
  menuNotLast: {
    borderRight: '1px solid black',
    ...(theme.mainMenuNotLast || {})
  }
})

class Menu extends PureComponent {
  handleClick = (menuItem) => {
    const { setMenu, order, actionRunning, operator } = this.props

    if (!_.isEmpty(actionRunning)) {
      // there is an action running ignore click
      return []
    }
    const id = (menuItem || {}).id
    const state = ((order || {})['@attributes'] || {}).state || ''
    switch (id) {
    case MENU_ORDER:
      if (_.isEmpty(operator)) {
        this.props.showInfoMessageAction('$NEED_TO_LOGIN_FIRST', '5000', 'error')
        return []
      }
      if (state === 'TOTALED') {
        return ['doBackFromTotal']
      }
      break
    case MENU_PAYMENT:
      return ['doTotal']
    case MENU_MANAGER:
      return ['doAuthorize']
    default:
      break
    }

    setMenu(id)
    return []
  }

  render() {
    const { classes, setMenu, menu, currentMenu, themeName } = this.props

    return (
      <div className={classes.menuContainer}>
        {_.map(menu, (menuItem, idx) => {
          const pressed = (currentMenu === menuItem.id)
          const clazz = (pressed) ? classes.menuActive : ''
          const notLast = (idx !== menu.length - 1) ? classes.menuNotLast : ''
          return (
            <Button
              key={`${menuItem.id}-${pressed}-${themeName}`}
              className={`${classes.menuButton} ${classes.menu} ${clazz} ${notLast}`}
              executeAction={() => this.handleClick(menuItem)}
              onActionFinish={(resp) => {
                if (resp === 'True') {
                  setMenu(menuItem.id)
                }
              }}
              text={menuItem.text}
              defaultText={menuItem.defaultText}
            />
          )
        })}
      </div>
    )
  }
}

Menu.propTypes = {
  classes: PropTypes.object.isRequired,
  showInfoMessageAction: PropTypes.func,
  themeName: PropTypes.string,
  /**
   * Action to set current menu
   */
  setMenu: PropTypes.func.isRequired,
  /**
   * App state holding actions currently in progress
   * @ignore
   */
  actionRunning: PropTypes.object,
  /**
   * Order state from `orderReducer`
   */
  order: PropTypes.object,
  /**
   * Operator state from `operatorReducer`
   */
  operator: PropTypes.object,
  /**
   * Menu items
   */
  menu: PropTypes.array,
  /**
   * CurrentScreen state from `currentScreenReducer`
   */
  currentMenu: PropTypes.number
}

Menu.defaultProps = {
  order: {},
  operator: {}
}

function mapStateToProps({ actionRunning, order, operator, menu, currentMenu, custom }) {
  return {
    actionRunning,
    order,
    operator,
    menu,
    currentMenu,
    themeName: (custom || {}).THEME || 'default'
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setMenu: setMenuAction,
    showInfoMessageAction
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(Menu))
