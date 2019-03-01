import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import { I18N } from 'posui/core'
import { Button } from 'posui/button'
import injectSheet, { jss } from 'react-jss'
import Logo from './Logo'
import setMenuAction from '../actions/setMenuAction'
import { MENU_ORDER } from '../reducers/menuReducer'
import {bindActionCreators} from "redux";

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  container: {
    display: 'flex',
    width: '100%',
    height: '100%',
    alignItems: 'center',
    position: 'absolute'
  },
  leftPanel: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '0 0 0 5%'
  },
  centerPanel: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '0 15%',
    maxWidth: '200px'
  },
  rightPanel: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 0,
    padding: '0 5% 0 0'
  },
  clockButton: {
    borderRadius: '10px',
    backgroundColor: '#3e3c3c',
    color: '#e2dac7',
    height: '9vh',
    textTransform: 'uppercase'
  },
  signInButton: {
    borderRadius: '10px',
    backgroundColor: '#3e3c3c',
    color: '#e2dac7',
    height: '9vh',
    textTransform: 'uppercase'
  },
  version: {
    position: 'absolute',
    bottom: 10,
    right: 10
  },
  versionSpan: {
    color: theme.color,
    fontSize: '1.2vh'
  }
})

class SignInScreen extends PureComponent {
  handleInputChange = (value) => {
    this.setState({ inputValue: value })
  }

  render() {
    const { classes, actionRunning, operator, posState, setMenu } = this.props
    const custom = (this.props.custom || {})
    const busy = !_.isEmpty(actionRunning)
    const loggedIn = !_.isEmpty(operator) && operator.state !== 'LOGGEDOUT'
    const signInButtonText = (loggedIn) ?
      <I18N id="$SIGN_OUT" defaultMessage="Sign Out"/> :
      <I18N id="$SIGN_IN" defaultMessage="Sign In"/>
    return (
      <div className={classes.container}>
        <div className={classes.leftPanel}>
        </div>
        <div className={classes.centerPanel}>
          <Logo />
        </div>
        <div className={classes.rightPanel}>
          <Button
            className={classes.signInButton}
            disabled={busy}
            executeAction={() => ((loggedIn) ? ['logoffuser'] : ['loginuser'])}
            onActionFinish={(resp) => {
              if ( (resp === 'True') && loggedIn) {
                setMenu(MENU_ORDER)
              }
            }}
          >
            { signInButtonText }
          </Button>
        </div>
        <div className={classes.version}>
          <span className={classes.versionSpan}>
            Version: {custom.CODE_VERSION || posState.version}
          </span>
        </div>
      </div>
    )
  }
}

SignInScreen.defaultProps = {
  operator: {}
}

SignInScreen.propTypes = {
    /**
   * @ignore
   */
  setMenu: PropTypes.func,
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * App state holding actions currently in progress
   * @ignore
   */
  actionRunning: PropTypes.object,
  /**
   * App Operator state
   * @ignore
   */
  operator: PropTypes.object,
  /**
   * App POS state
   * @ignore
   */
  posState: PropTypes.object,
  /**
   * App Custom state
   * @ignore
   */
  custom: PropTypes.object
}

function mapStateToProps(state) {
  return {
    actionRunning: state.actionRunning,
    operator: state.operator,
    posState: state.posState,
    custom: state.custom
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setMenu: setMenuAction
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(SignInScreen))
