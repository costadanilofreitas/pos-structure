// import React, { Component } from 'react'
// import { bindActionCreators } from 'redux'
// import { connect } from 'react-redux'
// import Grid from '../../layout/grid'
// import CouponImg from '../../images/1-Produto/BK_Offers1.jpg'
// import { COUPON_KEYBOARD } from '../../constants'
// import { changeScreenAction, changeTextTop } from '../../../actions'


// const couponMock = [
//     {
//         id: 1,
//         couponCode: 111,
//         text: '2 Saunduíches por R$ 15,00',
//         couponImg: CouponImg
//     },
//     {
//         id: 2,
//         couponCode: 222,
//         text: 'BK MIX R$ 5,00',
//         couponImg: CouponImg
//     }]

// export class OnSale extends Component {
//     constructor(props) {
//         super(props)
//         this.state = {

//         }
//     }

//     handleCouponClick(coupon) {
//         const newState = {
//             selectedCoupon: coupon
//         }
//         this.setState(newState)
//     }

//     handleIncludeCouponClick() {
//         this.props.changeScreenAction(COUPON_KEYBOARD)
//         this.props.changeTextTop(this.props.strings.TYPE_COUPON_CODE)
//     }

//     renderCoupons() {
//         return _.map(couponMock, (coupon) => {
//             return (
//                 <div key={coupon.id} className="bg-produto-offer text-center" onClick={() => this.handleCouponClick(coupon)}>
//                     <img src={coupon.couponImg} className="width-produto-king" alt="bg" />
//                 </div>
//             )
//         })
//     }

//     render() {
//         return (
//             <Grid cols='9 9 9' className="rolagem" >
//                 <div onClick={() => this.handleIncludeCouponClick()}>
//                     <Grid cols='12 12 12' className="div-btns-resumo-cupom" >
//                         <Grid cols='6 6 6' className="text-left" >
//                             <div className="btn-cupom  text-btn-resumo">{this.props.strings.CHOOSE_COUPON}</div>
//                         </Grid>
//                     </Grid>
//                 </div>
//                 <Grid cols='12 12 12' className="produtos" >
//                     {this.renderCoupons()}
//                 </Grid>
//             </Grid>
//         )
//     }
// }

// function mapStateToProps(state) {
//     return {
//         order: state.order,
//         // selectedSideMenu: state.selectedSideMenu,
//         strings: state.strings
//     }
// }

// function mapDispatchToProps(dispatch) {
//     return bindActionCreators({
//         changeScreenAction,
//         changeTextTop
//     }, dispatch)
// }

// export default connect(mapStateToProps, mapDispatchToProps)(OnSale)
