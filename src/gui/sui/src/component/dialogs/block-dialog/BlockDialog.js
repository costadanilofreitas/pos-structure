import React, { Component } from 'react'
import PropTypes from 'prop-types'

import BlockDialogRenderer from './block-dialog-renderer'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'


class BlockDialog extends Component {
  constructor(props) {
    super(props)

    this.state = {
      currentTime: null,
      showSpinner: false,
      type: ((this.props.staticConfig || {}).spinnerConfig || {}).type
    }

    this.checkActionError = this.checkActionError.bind(this)
    setTimeout(() => this.checkActionError(false), 5000)
  }

  checkActionError() {
    if (this.state.currentTime != null) {
      if ((new Date() - this.state.currentTime) > 180000) {
        window.location.reload(true)
      }
    }

    setTimeout(() => this.checkActionError(false), 5000)
  }

  static getDerivedStateFromProps(nextProps) {
    const actionIsRunning = !!nextProps.actionRunning && !!nextProps.actionRunning.busy
    const hasNotDialog = nextProps.dialogs.length === 0

    let enabled = false
    if (nextProps.staticConfig != null && nextProps.staticConfig.spinnerConfig != null) {
      enabled = nextProps.staticConfig.spinnerConfig.enabled
    }

    let currentTimer = null
    const showSpinner = actionIsRunning && hasNotDialog && enabled === true
    if (showSpinner) {
      currentTimer = new Date()
    }

    return ({
      currentTime: currentTimer,
      showSpinner: showSpinner,
      type: ((nextProps.staticConfig || {}).spinnerConfig || {}).type
    })
  }

  shouldComponentUpdate(nextProps, nextState) {
    return (this.state.showSpinner !== nextState.showSpinner || this.state.type !== nextState.type)
  }

  render() {
    if (this.state.showSpinner === true) {
      if (this.state.type === 'defaultSpinner') {
        return <BlockDialogRenderer/>
      }
    }

    return null
  }
}

BlockDialog.propTypes = {
  actionRunning: PropTypes.object,
  dialogs: PropTypes.array,
  staticConfig: StaticConfigPropTypes
}

export default BlockDialog
