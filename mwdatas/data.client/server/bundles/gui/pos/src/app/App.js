import React, { PureComponent } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { LoadingScreen, ScreenSize, Footer } from 'posui/widgets'
import { setThemeAction } from 'posui/actions'
import { DialogList } from 'posui/dialogs'
import injectSheet, { jss } from 'react-jss'
import { loadProductDataAction } from '../actions'
import { themes } from '../constants/themes'
import { Menu, MainScreen } from '.'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = (theme) => ({
  flexContainerStyle: {
    backgroundColor: theme.backgroundColor,
    height: '100%',
    width: '100%',
    display: 'flex',
    flexDirection: 'column'
  },
  menuContainerStyle: {
    flexGrow: 7,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  containerStyle: {
    flexGrow: 90,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative'
  },
  footerContainerStyle: {
    flexGrow: 3,
    flexShrink: 0,
    flexBasis: 0
  },
  trainingMode: {
    backgroundColor: 'darksalmon'
  }
})

class App extends PureComponent {
  constructor(props) {
    super(props)
    this.setCurrentTheme(props)
    props.loadProductDataAction()
  }

  setCurrentTheme = (props) => {
    const theme = _.get(props, 'custom.THEME', 'default')
    props.setThemeAction(_.find(themes, ['name', theme]))
  }

  componentDidUpdate(prevProps) {
    if (_.get(prevProps, 'custom.THEME', 'default') !== _.get(this.props, 'custom.THEME', 'default')) {
      this.setCurrentTheme(this.props)
    }
  }

  render() {
    const { classes, trainingMode } = this.props
    return (
      <LoadingScreen style={{ height: '100%' }}>
        <div className={(trainingMode) ? `${classes.flexContainerStyle} ${classes.trainingMode}` : classes.flexContainerStyle}>
          <div className={classes.menuContainerStyle}>
            <Menu />
          </div>
          <div className={classes.containerStyle}>
            <MainScreen />
          </div>
          <div className={classes.footerContainerStyle}>
            <Footer showDrawer={true}/>
          </div>
        </div>
        <ScreenSize />
        <DialogList />
      </LoadingScreen>
    )
  }
}

App.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  custom: PropTypes.object,
  trainingMode: PropTypes.bool,
  setThemeAction: PropTypes.func,
  loadProductDataAction: PropTypes.func
}

function mapStateToProps({ custom, trainingMode }) {
  return {
    custom,
    trainingMode
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setThemeAction,
    loadProductDataAction
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(App))
