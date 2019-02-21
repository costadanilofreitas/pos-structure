import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { padZeros } from '../../common'


const textStyle = {
    color: "#3a1b0a"
}

export class OrderItems extends Component {
    getSize(size) {
        return {
            'S': '(PEQ)',
            'M': '(MED)',
            'L': '(GDE)'
        }[size] || ''
    }
    renderOrderItems = () => {
        return _.map(this.props.order.items, (item, index) => {
            return (
                <div key={item.line} className={`pai-box-produto${this.props.scroll ? ' rolagem show-scroll' : ''}`} style={{paddingLeft: 0, height: 140, position: 'relative'}} onClick={() => this.props.onItemClick(item)}>
                    <div className="bg-top-detalhe"></div>
                    <div className="box-produto-rodape">
                        <div className="font-index descricao" style={textStyle}>
                            <p className="titulo-produto titulo-produto-rodape">{`0${item.currentQuantity} ${item.localizedName} ${this.getSize(item.size)}`}</p>
                            {this.renderOrderItemsDetails(item || [])}
                        </div>
                    </div>
                    <p className="titulo-produto-rodape valor-produto-rodape">
                        {`R$ ${(parseFloat(item.totalPrice) * item.currentQuantity).toLocaleString(this.props.strings.LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                    </p>
                </div>
            )
        });
    }

    renderOrderItemsDetails = (rootItem, item = rootItem, parent = null) => {
        return _.map(item.sons, (details) => {
            if (details.ignore) {
                return false
            }
            if (details.partType == 'Product') {
                if (item.partType == 'Combo' && ((item.cfh && (item.currentQuantity || 0) > 0) || ((details.currentQuantity || 0) !== details.defaultQuantity))) {
                    return (
                        <p key={`details_${item.partCode}_${details.partCode}`} className="preco-porcao">
                            {`${padZeros((details.currentQuantity || 1) * rootItem.currentQuantity, 2)} ${details.localizedName || details.name} ${this.getSize(details.size)}`}
                        </p>
                    )
                }
                else if (parent) {
                    if (parent.partType == 'Product' && (details.currentQuantity || 0) !== details.defaultQuantity) {
                        return (
                            <p key={`details_${item.partCode}_${details.partCode}`} className="preco-porcao ingredient">
                                {`${(details.currentQuantity > 0) ? `+${padZeros((details.currentQuantity - details.defaultQuantity) * rootItem.currentQuantity, 2)}` : 'SEM'} ${(details.localizedName || details.name)} ${this.getSize(details.size)}`}
                            </p>
                        )
                    }
                    else if (parent.partType == 'Combo' && details.currentQuantity > 0) {
                        return ([
                            <p key={`details_${item.partCode}_${details.partCode}`} className="preco-porcao">
                                {`${padZeros((details.currentQuantity) * rootItem.currentQuantity, 2)} ${(details.localizedName || details.name)} ${this.getSize(details.size)}`}
                            </p>
                        , ...this.renderOrderItemsDetails(rootItem, details, item)])
                    }
                }
            }
            else if (details.partType == 'Combo' && !details.cfh) {
                return (
                    <p key={`details_${item.partCode}_${details.partCode}`} className="preco-porcao">
                        {`${padZeros((details.currentQuantity || 1) * rootItem.currentQuantity, 2)} ${(details.localizedName || details.name)} ${this.getSize(details.size)}`}
                    </p>
                )
            }
            if (details.partType === 'Combo' || details.partType === 'Option' || details.currentQuantity > 0) {
                return this.renderOrderItemsDetails(rootItem, details, item)
            }

        });
    }

    render() {
        return (<div style={{ width: '100%', marginLeft: '10px' }}>{this.renderOrderItems()}</div>)
    }

}

function mapStateToProps(state) {
    return {
        order: state.order,
        strings: state.strings
    }
}

export default connect(mapStateToProps)(OrderItems)