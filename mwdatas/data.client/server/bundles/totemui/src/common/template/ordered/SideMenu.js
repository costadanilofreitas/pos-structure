import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import ReactLoading from 'react-loading'
import Color from 'color'
import _ from 'lodash'
import sidebarImage from '../../images/categoria/promocao/img_promocoes_defaut.png'
import sidebarBG from '../../images/bg_defaut.png'
import selectedBG from '../../images/categoria/bebida/bg_bebidas.png'
import { changeTextTop, SetProductFromSuggestionAction, selectMenuCategoryAction, categoryAllAction, productInCategoryAction, changeSubScreenAction, setCategoryScroll } from '../../../actions'
import { BASE_URL, ON_SALE_SCREEN } from '../../../common/constants';

export class SideMenu extends Component {
	constructor(props) {
		super(props)
		this.state = {
			scrollValue: 0,
			scrollClass: "hide-scroll",
		}
	}
	handleButtonClick = (button) => {
		this.props.selectMenuCategoryAction(button)
		this.props.productInCategoryAction(button.id)
		this.props.changeTextTop(this.props.strings.CHOOSE_HERE)
	}

	chooseContrastColor = (originalColor) => {
		let bgColor = new Color(originalColor)
		return (bgColor.luminosity() > 0.32) ? '#000000' : '#FFFFFF'
	}

	renderButtons = () => {

		if (!this.props.allCategorys || this.props.allCategorys.length === 0) {
			return (
				<ReactLoading type="spin" color="#444" />
			)
		}

		return _.map(this.props.allCategorys, (button, index) => {
			const buttonSelected = this.props.selectedSideMenu && button.id == this.props.selectedSideMenu.id;
			const name = ((new DOMParser().parseFromString((button.name || "").toLowerCase(), "text/html")).documentElement.textContent).toUpperCase()
			return (
				<center key={index} onClick={() => button.enabled ? this.handleButtonClick(button) : null}>

					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 135.1 129.69" width="180px" height="190px" version="1.1">
						<g transform="translate(-26.384 -60.388)">
							<path fill={buttonSelected ? button.color : '#ddd'} d="m 26.46 66.079 c 0.13364 -1.8709 -0.19034 -5.5032 6.1472 -4.5436 c 9.3429 1.4147 35.269 -0.39626 44.099 -1.0691 c 7.0158 -0.53454 29.074 1.8489 42.229 1.3363 c 5.1449 -0.20045 28.287 0.69238 35.28 -0.26727 c 6.9923 -0.95965 7.4835 1.6036 7.2163 6.949 c -0.26727 5.3454 -0.26727 70.559 -0.26727 70.559 s -0.36789 42.236 -0.0668 44.768 c 0 0 -0.10475 0.94395 -0.0554 1.8715 c 0.12626 2.3738 -0.82533 3.0592 -2.7076 3.5366 c -3.3559 0.85111 -23.63 -0.79771 -31.915 0.0709 c -7.4854 0.78476 -25.274 1.0636 -30.936 0.46772 c -5.7701 -0.60722 -33.425 -1.0858 -38.821 -1.4032 c -5.6795 -0.33408 -16.648 0.004 -23.52 0.93545 c -6.8721 0.93134 -6.949 -1.6036 -6.6817 -6.1472 s 0 -89.803 0 -89.803 Z" />
						</g>
					</svg>

					<div style={{ position: 'absolute', marginTop: -180, width: '180px' }}>
						<div style={{ width: "120px", height: "100px", display: "block", margin: "auto", position: "relative", marginTop: '10px'}}>
							<img src={BASE_URL + button.imageUrl} alt="bg" className="img-menu-lateral" style={{maxHeight: '100px', maxWidth: '120px', width: 'auto', height: 'auto', margin: 'auto', marginBottom: '10px', bottom: 0, right: 0, left: 0, position: 'absolute'}} />
						</div>
						{/*<img src={BASE_URL + button.imageUrl} className="img-menu-lateral" alt="bg" style={{maxHeight: '120px', maxWidth: '120px', width: 'auto', height: 'auto'}} />*/}

						<p className="font-index titulo-menu-lateral" style={{ color: this.chooseContrastColor(buttonSelected ? button.color : '#ddd'), width: `${button.name == 'ACOMPANHAMENTOS' ? '180px ' : '135px'}` }} dangerouslySetInnerHTML={{__html: name}} />
					</div>
				</center>
			)
		});

	}

	handleScroll() {
		if (this.scrollTimeout) {
			clearTimeout(this.scrollTimeout)
		}
		this.props.setCategoryScroll(this.mainDiv.scrollTop)
		this.setState({scrollClass: "show-scroll"})

		this.scrollTimeout = setTimeout(this.hideScroll, 1000)
	}
	hideScroll = () => {
		console.log("chegou aqui")
		this.setState({scrollClass: "hide-scroll"})
		this.scrollTimeout = null
	}
	componentDidMount() {
		this.mainDiv.scrollTop = this.props.categoryScroll
	}

	componentWillUnmount() {
		if (this.scrollTimeout) {
			clearTimeout(this.scrollTimeout)
		}
	}
	render() {
		return (
			<div id="MenuLateral">
				<div ref={(el) => this.mainDiv = el} className={`col-sm-3 col-md-3 rolagem menu-lateral ${this.state.scrollClass}`} onScroll={() => this.handleScroll()}>
					{this.renderButtons()}
				</div>
			</div>
		)
	}
}

function mapStateToProps(state) {
	return {
		strings: state.strings,
		order: state.order,
		selectedSideMenu: state.selectedSideMenu,
		allCategorys: state.category.allCategorys,
		categoryScroll: state.categoryScroll
	}
}

function mapDispatchToProps(dispatch) {
	return bindActionCreators({
		changeTextTop,
		SetProductFromSuggestionAction,
		selectMenuCategoryAction,
		categoryAllAction,
		productInCategoryAction,
		changeSubScreenAction,
		setCategoryScroll
	}, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(SideMenu)