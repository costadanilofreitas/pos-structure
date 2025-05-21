import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import styled from 'styled-components'

import { setDisplayModeAction } from '../../../../actions'
import withState from '../../../../util/withState'

const IconWrapper = styled.div`
  margin-left: 1em;
`

class DisplayModeChanger extends PureComponent {
  constructor(props) {
    super(props)

    this.handleClickChangeDisplay = this.handleClickChangeDisplay.bind(this)
  }

  render() {
    const { icon, changeTo: mode, className } = this.props

    return (
      <IconWrapper>
        <i className={`${icon} ${className}`} onClick={() => this.handleClickChangeDisplay(mode)}/>
      </IconWrapper>
    )
  }

  handleClickChangeDisplay(mode) {
    const { displayMode, setDisplayMode } = this.props
    setDisplayMode(displayMode === mode ? 'normal' : mode)
  }
}

DisplayModeChanger.propTypes = {
  displayMode: PropTypes.string,
  setDisplayMode: PropTypes.func,
  icon: PropTypes.string,
  changeTo: PropTypes.string,
  className: PropTypes.string
}


function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setDisplayMode: setDisplayModeAction
  }, dispatch)
}

export default withState(DisplayModeChanger, mapDispatchToProps, 'displayMode')
