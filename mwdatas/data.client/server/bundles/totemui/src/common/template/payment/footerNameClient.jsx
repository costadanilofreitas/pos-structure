// import React, { Component } from 'react'
// import { bindActionCreators } from 'redux'
// import { connect } from 'react-redux'
// import { NAME_SCREEN, PAYMENT_FORM_SCREEN } from '../../constants'
// import { changeScreenAction, changeTextTop, modalAction, saleAddCustomerInfoAction } from '../../../actions'
// import Modal from '../../msg/modal'


// const textStyle = {
//     color: "#3a1b0a"
// }

// export class FooterNameCLient extends Component {
//     constructor(props) {
//         super(props);
//         this.state = {
//             titleHeader: "Atenção!",
//             titleBody: "",
//             divCenter: "",
//             divFooter: ""

//         };
//     }

//     handlerConfirm = () => {
//         if (this.props.order.clientName.length == 0) {
//             this.setState({
//                 titleHeader: "Atenção!",
//                 titleBody: "",
//                 divCenter: "Digite seu nome!"

//             });
//             this.props.modalAction("show")
//         }
//         else {
//             this.props.saleAddCustomerInfoAction(this.props.order.sale_token, {
//                 "name": this.props.order.clientName,
//                 "document": this.props.order.cpf
//             }).then(() => {
//                 this.props.changeScreenAction(PAYMENT_FORM_SCREEN);
//             })
//         }
//     }

//     render() {
//         return (
//             <footer>
//                 <div className="max-width">
//                     <div id="detalhePedido" className="row resumo-pedido-open-fluxo">
//                         <div className="col-sm-12 col-md-12  div-btns-resumo">
//                             <div className="row">
//                                 <div className="col-sm-6 col-md-6 text-left">
//                                     <div className="btn-cancelar-pedido text-center">
//                                         <span className="text-btn-resumo">{this.props.strings.CANCEL}</span>
//                                     </div>

//                                 </div>
//                                 <div className="col-sm-6 col-md-6 text-left">
//                                     <div className="btn-finalizar-pedido text-center">
//                                         <span className="text-btn-resumo" onClick={this.handlerConfirm} >{this.props.strings.CONFIRM}</span>
//                                     </div>
//                                 </div>

//                             </div>
//                         </div>
//                     </div>
//                 </div>
//                 <Modal type={"alert"} titleHeader={this.state.titleHeader} titleBody={this.state.titleBody} divCenter={this.state.divCenter} />
//             </footer>
//         )
//     }
// }

// function mapStateToProps(state) {
//     return {
//         selectedScreen: state.selectedScreen,
//         order: state.order,
//         strings: state.strings
//     }
// }

// function mapDispatchToProps(dispatch) {
//     return bindActionCreators({
//         changeScreenAction,
//         modalAction,
//         saleAddCustomerInfoAction
//     }, dispatch)
// }


// export default connect(mapStateToProps, mapDispatchToProps)(FooterNameCLient)