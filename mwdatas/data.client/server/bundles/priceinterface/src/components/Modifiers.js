import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import { Panel, PanelGroup } from 'react-bootstrap'

import { UserPropTypes } from '../reducers/reducers'
import { ModifierClassPropType } from '../reducers/modifiersReducer'
import { GET_MODIFIERS_REQUEST, PRICE_MODIFIERS } from '../common/constants'

import GenericList from './GenericList'
import { logoutUser } from '../actions/userActions'


class Modifiers extends Component {
  constructor(props) {
    super(props)
    this.state = {
      open: false,
      key: null
    }
  }

  componentWillMount() {
    this.props.getAllModifiers(this.props.user.token)
    if (this.props.modifiersList
        && this.props.modifiersList.loadingData !== undefined
        && this.props.modifiersList.loadingData === false
        && this.props.modifiersList.data
        && this.props.modifiersList.data.response
        && this.props.modifiersList.data.response.status === 401) {
      this.props.logoutUser(this.props.user.token)
    }
  }

  componentDidUpdate() {
    if (this.props.modifiersList
        && this.props.modifiersList.loadingData !== undefined
        && this.props.modifiersList.loadingData === false
        && this.props.modifiersList.data
        && this.props.modifiersList.data.response
        && this.props.modifiersList.data.response.status === 401) {
      this.props.logoutUser(this.props.user.token)
    }
  }

  render() {
    return (
      (this.props.modifiersList
       && this.props.modifiersList.loadingData !== undefined
       && this.props.modifiersList.loadingData === true)
        ? <h3 className="loadingDiv"> Carregando Dados </h3>
        : this.props.modifiersList
          && this.props.modifiersList.data
          && this.props.modifiersList.data.response
          && this.props.modifiersList.data.response.status !== 200
        ? <div>
          <h3>Erro ao carregar os dados</h3>
          <p> Erro: {this.props.modifiersList.data.message} </p>
        </div>
        :
        <PanelGroup accordion id="modifierPanel" className="panelModifier" >
        { this.props.modifiersList
          && this.props.modifiersList.data
          && this.props.modifiersList.data.map((modifiers, iModifier) =>
           <Panel eventKey={ iModifier }
              key={ iModifier + '_' + modifiers.name } >
               <Panel.Heading >
                  <Panel.Title toggle >{ modifiers.name }</Panel.Title>
               </Panel.Heading>
                <Panel.Body collapsible>
                   <PanelGroup accordion id="modifierClass" className="panelmodifierClass">
                     { modifiers && modifiers.modifiersClass.map((modifierClass, iClass) =>
                        <Panel eventKey={ iClass } key={ iClass + '_' + modifierClass.name + '_' + modifierClass.classCode }>
                          <Panel.Heading>
                           <Panel.Title toggle onClick={()=>this.setState({ open: true, key: iClass + '_' + modifierClass.name + '_' + modifierClass.classCode })}>
                             {modifierClass.name}
                             <span style={{ display: 'none' }}>{modifierClass.classCode}</span>
                           </Panel.Title>
                          </Panel.Heading>
                          <Panel.Body collapsible key={ iClass + '_' + modifierClass.name + '_' + modifierClass.classCode }>
                            { this.state.open
                              && this.state.key === iClass + '_' + modifierClass.name + '_' + modifierClass.classCode &&
                              <GenericList
                                key={ iClass + '_' + modifierClass.name + '_' + modifierClass.classCode }
                                dataRequest={ `${PRICE_MODIFIERS}${modifierClass.classCode}` }
                                classCode={ modifierClass.classCode }/>
                            }
                            </Panel.Body>
                        </Panel>)}
                      </PanelGroup>
                    </Panel.Body>
                </Panel>
        )
        }
      </PanelGroup>
    )
  }
}

Modifiers.propTypes = {
  modifiersList: PropTypes.arrayOf(ModifierClassPropType),
  getAllModifiers: PropTypes.func,
  user: UserPropTypes,
  logoutUser: PropTypes.func
}

Modifiers.defaultProps = {
  modifiersList: null,
  user: UserPropTypes
}

const mapStateToProps = (state) => {
  return {
    modifiersList: state.modifiersList,
    user: state.user
  }
}

const mapDispatchToProps = dispatch => {
  return {
    getAllModifiers: (token) => dispatch({
      type: GET_MODIFIERS_REQUEST,
      token: token
    }),
    logoutUser: token => dispatch(logoutUser(token))
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(Modifiers)
