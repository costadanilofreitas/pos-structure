import React, { PureComponent } from 'react'
import Helmet from 'react-helmet'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import _ from 'lodash'
import { ThemeProvider as ReactThemeProvider } from 'react-jss'
import { ThemeProvider as StyleThemeProvider } from 'styled-components'

import { LoadingScreen, ScreenSize } from '3s-posui/widgets'
import { setThemeAction } from '3s-posui/actions'

import themes from '../constants/themes'

import MainScreen from './screen/main-screen'
import { loadKdsModelAction } from '../actions'
import loadThemeConfigurationAction from '../actions/loadThemeConfigurationAction'
import withState from '../util/withState'


class App extends PureComponent {
  constructor(props) {
    super(props)

    props.loadKdsModel()
    props.loadThemeConfigurationAction()

    this.kdsModel = this.props.kdsModel
    this.kdsModel.id = this.props.kdsId

    this.setCurrentTheme(props)
  }

  loadingScreenStyle = {
    height: '100%'
  }

  render() {
    const TITLE = `E-DEPLOY POS KUI [${this.props.kdsId}]`
    return (
      <ReactThemeProvider theme={this.props.theme}>
        <StyleThemeProvider theme={this.props.theme}>
          <Helmet>
            <title> {TITLE} </title>
          </Helmet>
          <LoadingScreen
            style={this.loadingScreenStyle}
            type="KDS"
            customLoadingFlag={this.isLoading()}
          >
            <MainScreen/>
            <ScreenSize/>
          </LoadingScreen>
        </StyleThemeProvider>
      </ReactThemeProvider>
    )
  }

  isLoading() {
    return (
      this.props.kdsId == null ||
      this.props.locale == null ||
      this.props.kdsModel == null ||
      this.props.kdsModel.layout == null ||
      this.props.kdsModel.layout.lines == null ||
      this.props.kdsModel.views == null ||
      this.props.refreshEnd === false
    )
  }

  setCurrentTheme = (props) => {
    const theme = _.get(props, 'custom.THEME', 'DEFAULT')
    props.setThemeAction(_.find(themes, ['name', theme]))
  }

  componentDidUpdate(prevProps) {
    if (_.get(prevProps, 'custom.THEME', 'default') !== _.get(this.props, 'custom.THEME', 'default')) {
      this.setCurrentTheme(this.props)
    }
  }

  componentDidCatch = (error, errorInfo) => {
    console.error(`APP JS ERROR: ${error.toString()}`)
    console.error(`APP JS ERROR_INFO: ${errorInfo.componentStack}`)
    setTimeout(() => window.location.reload(true), 5000)
  }
}

App.propTypes = {
  kdsId: PropTypes.number,
  theme: PropTypes.object,
  kdsModel: PropTypes.object,
  locale: PropTypes.object,
  loadKdsModel: PropTypes.func,
  loadThemeConfigurationAction: PropTypes.func,
  refreshEnd: PropTypes.bool
}

App.defaultProps = {
  theme: {},
  kdsModel: {}
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(
    {
      setThemeAction,
      loadKdsModel: loadKdsModelAction,
      loadThemeConfigurationAction: loadThemeConfigurationAction
    }, dispatch)
}

export default withState(App, mapDispatchToProps, 'kdsId', 'theme', 'kdsModel', 'locale', 'refreshEnd')
