import React, { Component } from 'react';
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import _ from 'lodash'
import TitleMain from '../../common/template/welcome/titleMain'
import MainSelection from '../../common/template/welcome/MainSelection'
import Ordered from '../../common/template/ordered/ordered'
import ModalError from '../../common/msg/modalError'
import { START_SCREEN, TYPE_SELECT_SCREEN, SALE_SCREEN, NAME_SCREEN, PAYMENT_SCREEN, PAYMENT_FORM_SCREEN, COUPON_KEYBOARD } from '../constants'
import { categoryAllAction, selectMenuCategoryAction, productInCategoryAction, getUrlBannerAction, changeScreenAction, getOptionsLabelAction, cleanUpAction, configAction, errorAction, alterTimeCounterAction, saleCancelAction } from '../../actions'

// idle time to restart screen flow
// const TIMEOUT_LIMIT = 40
// idle time to show modal
// const TIMEOUT_SHOW_MODAL = TIMEOUT_LIMIT - 6

export class App extends Component {
	constructor(props) {
		super(props);
		this.state = {
			waitModal: true,
			waitText: "O TOTEM ESTÁ SENDO INICIALIZADO.\nPOR FAVOR, AGUARDE\nOU DIRIJA-SE AO BALCÃO."
		}
	}
	getLabels() {
		this.props.getOptionsLabelAction().then((result)=>{
			if (result.error) {
				this.setState({waitModal: true})
				_.delay(()=>this.getLabels(), 1000)
			} else {
				this.setState({waitModal: false})
			}
		})
	}
	getBanners() {
		this.props.getUrlBannerAction().then((result)=>{
			if (result.error) {
				this.setState({waitModal: true})
				_.delay(()=>this.getBanners(), 1000)
			} else {
				this.setState({waitModal: false})
			}
		})
	}
	getConfig() {
		this.props.configAction().then((data) => {
			if (data.payload.message) {
				//this.props.errorAction(data)
				this.setState({waitModal: true})
				this.getConfig()
			} else {
				if (this.props.config.time === undefined) {
					this.setState({waitModal: true, waitText: "DADOS DO TOTEM INDISPONÍVEIS.\nPOR FAVOR, FAÇA A CARGA DE DADOS\nPELO MENU DO GERENTE."})
					_.delay(()=>this.getConfig(), 500)
				} else {
					this.setState({waitModal: false})
				}
			}
		})
	}
	componentWillMount = () => {
		window.setInterval(this.timerIncrement, 1000);//intervalo de 1s
		this.getLabels()
		this.getBanners()
		this.getConfig()
	}

	resetTimer = () => {
		this.props.alterTimeCounterAction(0)
	}

	timerIncrement = () => {
		if (this.props.selectedScreen == START_SCREEN) {
			return
		}
		this.props.alterTimeCounterAction(this.props.config.timeCounter + 1)

		if (this.props.config.timeCounter == this.props.config.time) {
			this.props.saleCancelAction(this.props.order.sale_token)
			this.props.changeScreenAction(START_SCREEN)
			this.resetTimer()
			return
		}

	}

	renderSelectedScreen = () => {
		switch (this.props.selectedScreen) {
			case START_SCREEN:
				return <TitleMain />
			case TYPE_SELECT_SCREEN:
				return <MainSelection />
			case SALE_SCREEN:
			case NAME_SCREEN:
			case PAYMENT_SCREEN:
			case PAYMENT_FORM_SCREEN:
			case COUPON_KEYBOARD:
			case PAYMENT_SCREEN:
				return <Ordered />
			default:
				return null
		}
	}

	renderTimeoutModal = () => {
		if (this.props.config.time === undefined || this.props.config.timeCounter < (this.props.config.time - 6) || (this.props.config.time - this.props.config.timeCounter) <= 0) {
			return null
		}
		return (
			<div className="modal show" id="myModal" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}  >
				<div className="vertical-alignment-helper">
					<div className="modal-dialog vertical-align-center" role="document">
						<div className="modal-content">
							<div id="contador" className="font-contador contador-numero">{this.props.config.time - this.props.config.timeCounter}</div>
							<div className="font-contador contador-text">{this.props.strings.SECONDS}</div>
						</div>
					</div>
				</div>
			</div>
		)
	}

	renderWaitModal() {
		return (
            <div className={'modal show'} tabIndex="-1" role="dialog" data-backdrop="static" data-keyboard="false" aria-labelledby="myModalLabel" style={{ backgroundColor: "rgba(100,100,100,0.6)" }}>
                <div className="vertical-alignment-helper">
                    <div className="modal-dialog vertical-align-center">
                        <div id="bodyModal" className="modal-selecao modal-content">
                            <div className="bg-modal">
                                <div className="bg-modal-int">
                                    <div className="modal-header">
                                        <div className="max-width row">
                                            <div className="form-inline">

                                                <div className="col-sm-10 col-md-8 text-left">
                                                    <h4 className="modal-title-cpf">CARREGANDO</h4>
                                                </div>

                                            </div>
                                        </div>
                                    </div>

                                    <div className="modal-body">
                                        <div className="max-width row">
                                            <div className="col-sm-12 col-md-12 ">
                                                <center>
                                                    <div style={{ marginTop: "50px", marginBottom: '50px' }}>
                                                        <span className="font-index" style={{ fontSize: '30px', whiteSpace: 'pre-line' }}>{this.state.waitText}</span>
                                                    </div>
                                                </center>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
	}
	verifyRender() {
		if (this.state.waitModal) {
			return this.renderWaitModal()
		} else if (this.props.error.menssageCode != '') {
			return <ModalError />
		} else {
			return (
				<div>
					{this.renderSelectedScreen()}
					{this.renderTimeoutModal()}
				</div>
			)
		}
	}

	render() {
		return (
			<div onTouchMove={() => this.resetTimer()} onClick={() => this.resetTimer()} >
				{this.verifyRender()}
			</div>
		)
	}
}

function mapStateToProps(state) {
	return {
		selectedScreen: state.selectedScreen,
		strings: state.strings,
		error: state.error,
		config: state.config,
		order: state.order
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		categoryAllAction,
		selectMenuCategoryAction,
		productInCategoryAction,
		changeScreenAction,
		getOptionsLabelAction,
		cleanUpAction,
		configAction,
		errorAction,
		alterTimeCounterAction,
		getUrlBannerAction,
		saleCancelAction
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(App)