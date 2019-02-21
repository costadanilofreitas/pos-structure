import React, { Component } from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import ReactLoading from 'react-loading'
import Banner1 from '../../../common/images/Banner/b1.jpg';
import Banner2 from '../../../common/images/Banner/b2.jpg';
import { registerProductAction, expandedFooterAction, changeSubScreenAction } from './../../../actions'
import { BASE_URL, PRODUCT_SCREEN, SALE_SCREEN, MAIN_SCREEN } from '../../../common/constants';

export class Header extends Component {

    constructor(props) {
        super(props)
        this.state = {
            indexImg: 0,
        }
    }

    loadLstBanner() {
        this.lstBannerFilter = this.props.urlBanner

        // this.lstBannerFilter = [Banner1, Banner2]
    }



    componentDidMount() {
        // this.loadBanners1()
        let atual = this.lstBannerFilter[this.state.indexImg]


        if (!atual && this.state.indexImg > 0) {
            this.setState({ indexImg: 0 })
        } else if (this.lstBannerFilter.length > 1) {
            this.initCarrocelBanner(this.state.indexImg)
        }
    }

    componentWillUnmount() {
        clearTimeout(this.setTimeout)
    }

    registreProduct(partCode) {
        this.props.registerProductAction(partCode)
        this.props.changeSubScreenAction(PRODUCT_SCREEN)
        this.props.expandedFooterAction(false)
    }

    initCarrocelBanner(index) {
        if (this.lstBannerFilter.length > 1) {
            let atual = this.lstBannerFilter[index]
            if (atual) {
                if (this.setTimeout) {
                    clearTimeout(this.setTimeout)
                }
                if (index >= this.lstBannerFilter.length - 1) {
                    this.setTimeout = setTimeout(() => {
                        this.setState({ indexImg: 0 })
                        this.initCarrocelBanner(0)
                    }, (atual.delay * 1000))
                } else {
                    this.setTimeout = setTimeout(() => {
                        index++
                        this.setState({ indexImg: index })
                        this.initCarrocelBanner(index)

                    }, (atual.delay * 1000))
                }
            }
        }
    }

    loadBanners1() {
        this.setTimeout = setTimeout(() => {
            this.setState({ indexImg: 1 })
            this.loadBanners2()
        }, 5000)
    }

    loadBanners2() {
        this.setTimeout =  setTimeout(() => {
            this.setState({ indexImg: 0 })
            this.loadBanners1()
        }, 5000)
    }

    handleBannerClick = () => {
        const bannerAtual = this.lstBannerFilter[this.state.indexImg]
        if (bannerAtual.partcode > 0 &&
           this.props.selectedScreen == SALE_SCREEN &&
           this.props.selectedSubScreen == MAIN_SCREEN) {
            this.registreProduct(bannerAtual.partcode)
        }
    }

    render() {
        this.loadLstBanner()

        let bannerAtual = this.lstBannerFilter[this.state.indexImg]

        return (
            <header className="row row-ordered">
                <div className="banner-dimension">
                    {
                        bannerAtual &&
                        <img src={BASE_URL + bannerAtual.imageUrl} alt="Banner" onClick={this.handleBannerClick} />
                    }


                    {/*<img src={this.lstBannerFilter[this.state.indexImg]} style={{ width: '100%' }} alt="Banner" />*/}
                </div>
            </header>
        )
    }
}

function mapStateToProps(state) {
    return {
        urlBanner: state.header.urlBanner,
        selectedSideMenu: state.selectedSideMenu,
        selectedScreen: state.selectedScreen,
        selectedSubScreen: state.selectedSubScreen
    }
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({
        registerProductAction,
        expandedFooterAction,
        changeSubScreenAction
    }, dispatch)
}

export default connect(mapStateToProps, mapDispatchToProps)(Header)