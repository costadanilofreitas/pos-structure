import React, { Component } from 'react';
import Order from './Order';
import Retransmit from './Retransmit';
import {calculateColumns as calculateOrderColumns} from './OrderItems';
import {calculateColumns as calculateRetransmitColumns} from './RetransmitItems';


class OrderList extends Component {
    render() {
        ////this.props.orderPagesUpdated(this.state.currentPage, pageIndex);

        let orderClassNames = "col-md-3 col-sm-12";
        let orderClassDoubleNames = "col-md-6 col-sm-12";
        let orderClassTripleNames = "col-md-9 col-sm-12";
        let orderClassQuadNames = "col-md-12 col-sm-12";
        if (this.props.smallSize) {
            orderClassNames = "col-md-12 hidden-sm hidden-xs";
        }

        let rowIndexKey = 0;
        return (
            <div className="order-list">
                {this.props.page.map(row =>
                    <div key={rowIndexKey++} className="row order-row">
                        {row.map(order => {
                            const isReentrega = order.partner.includes('reentrega')
                            let numberOfColumns = (isReentrega ? calculateRetransmitColumns : calculateOrderColumns)(order);

                            let correctClassNames = orderClassNames;
                            if(!this.props.smallSize) {
                                if (numberOfColumns === 2) {
                                    correctClassNames = orderClassDoubleNames;
                                }
                                else if (numberOfColumns === 3) {
                                    correctClassNames = orderClassTripleNames;
                                }
                                else if (numberOfColumns > 3) {
                                    correctClassNames = orderClassQuadNames;
                                }
                            }
                            const OrderObject = isReentrega ? Retransmit : Order
                            return (<div key={`${isReentrega ? `retransmit_${order.originatorID}` : 'order'}_${order.id}`} className={correctClassNames}>
                                <OrderObject {...order} sendOrderToProduction={this.props.sendOrderToProduction} reprintOrder={this.props.reprintOrder} smallSize={this.props.smallSize}/>
                            </div>)
                        })}
                    </div>
                )}
            </div>
        )
    }
}

export default OrderList;
