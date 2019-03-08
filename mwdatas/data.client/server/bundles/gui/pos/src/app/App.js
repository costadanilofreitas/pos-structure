import React, { PureComponent } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import _ from 'lodash'
import { LoadingScreen, ScreenSize, Footer } from 'posui/widgets'
import { setThemeAction } from 'posui/actions'
import { DialogList } from 'posui/dialogs'
import { MessageBus } from 'posui/core'
import injectSheet, { jss } from 'react-jss'
import { loadProductDataAction } from '../actions'
import themes from '../constants/themes'
import { Menu, MainScreen, CustomMessageDialog } from '.'

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
    this.msgBus = new MessageBus(props.posId)
    this.setCurrentTheme(props)
    props.loadProductDataAction()
    this.state = {
      loading: false
    }
  }

  setCurrentTheme = (props) => {
    const theme = _.get(props, 'custom.THEME', 'default')
    props.setThemeAction(_.find(themes, ['name', theme]))
  }

  checkOnline = () => {
    this.msgBus.syncAction('isPyscriptsOnline')
      .then((response) => {
        if (response.data === 'True') {
          this.setState({ loading: false })
          clearInterval(this.timerId)
          this.timerId = null
        } else {
          this.setState({ loading: true })
        }
      })
  }

  componentDidUpdate(prevProps) {
    if (_.get(prevProps, 'custom.THEME', 'default') !== _.get(this.props, 'custom.THEME', 'default')) {
      this.setCurrentTheme(this.props)
    }
    const prevSynched = _.get(prevProps, 'loading.synched', false)
    const synched = _.get(this.props, 'loading.synched', false)
    if (prevSynched !== synched) {
      if (!synched) {
        this.setState({ loading: true })
        return
      }
      if (this.timerId) {
        clearInterval(this.timerId)
      }
      this.timerId = setInterval(this.checkOnline, 1000)
    }
  }

  render() {
    const { classes, trainingMode } = this.props
    const { loading } = this.state
    return (
      <LoadingScreen style={{ height: '100%' }} customLoadingFlag={loading}>
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
        <DialogList customDialogs={{ messagebox: CustomMessageDialog }} />
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
  loadProductDataAction: PropTypes.func,
  posId: PropTypes.number.isRequired,
  loading: PropTypes.object.isRequired
}

function mapStateToProps({ custom, trainingMode, loading, posId }) {
  return {
    custom,
    trainingMode,
    loading,
    posId
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setThemeAction,
    loadProductDataAction
  }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(injectSheet(styles)(App))
