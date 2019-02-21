import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import { logoutUser } from '../actions/userActions'
import { UserPropTypes } from '../reducers/reducers'


class TitleBar extends Component {
  render() {
    return (
      <div className="row titleBar">
        <div className="col-lg-6 col-md-6 col-xs-6 float-left">
          <div className="logoBox"/>
        </div>
        <div className="col-lg-6 col-md-6 col-xs-6 float-right userInfoBox">
            {this.renderLogedUserInfo()}
        </div>
      </div>
    )
  }

  renderLogedUserInfo() {
    if (this.props.user != null) {
      return (
        <div className="logedUserInfo float-right">
          <p>Bem Vindo,</p>
          <p className="nameUser">{this.props.user.username}</p>
          <p className="logoutLine" onClick={ this.logoutClick.bind(this) }>
            <span>logout</span>
            <span className="logoutButton" />
          </p>
        </div>
      )
    }

    return ''
  }

  logoutClick() {
    this.props.logoutUser(this.props.user.token)
  }
}

TitleBar.propTypes = {
  user: UserPropTypes,
  logoutUser: PropTypes.func
}

const mapStateToProps = state => (
  {
    user: state.user
  })

const mapDispatchToProps = dispatch => (
  {
    logoutUser: (token) => dispatch(logoutUser(token))
  })

export default connect(mapStateToProps, mapDispatchToProps)(TitleBar)
