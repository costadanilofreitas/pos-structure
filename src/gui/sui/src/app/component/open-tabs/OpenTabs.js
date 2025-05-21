import React, { Component } from 'react'
import PropTypes from 'prop-types'
import WorkingModePropTypes from '../../../prop-types/WorkingModePropTypes'
import { isCashierFunction } from '../../model/modelHelper'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'
import { IconStyle, CommonStyledButton } from '../../../constants/commonStyles'


export default class OpenTabs extends Component {
  constructor(props) {
    super(props)

    this.handleOnClick = this.handleOnClick.bind(this)
  }

  render() {
    const { workingMode, staticConfig } = this.props
    const disabled = isCashierFunction(workingMode) || !staticConfig.enableTabBtns

    return (
      <CommonStyledButton
        className={'test_OpenTabs_CREATE-TAB'}
        key="addOrder"
        text="$CREATE_TAB"
        disabled={disabled}
        executeAction={() => this.handleOnClick()}
        border={true}
      >
        <IconStyle className="fas fa-pager fa-2x" aria-hidden="true"/>
        <br/>
      </CommonStyledButton>
    )
  }

  handleOnClick() {
    if (this.props.checkAndToggleTableInfo != null) {
      this.props.checkAndToggleTableInfo()
    }
    return ['open_tab']
  }
}

OpenTabs.propTypes = {
  workingMode: WorkingModePropTypes,

  checkAndToggleTableInfo: PropTypes.func,
  staticConfig: StaticConfigPropTypes
}
