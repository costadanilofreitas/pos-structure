import React, { Component } from 'react';

class Espelho extends Component {
    render() {
        const orderList = this.props.pickupList.sort((a, b)=> b.displayCount - a.displayCount);
        const elementsLevel0 = orderList.slice(0,1).map((one_order, index) =>
            <div key={index} className='pickup-new-block1-sub1-elem'>{one_order.customer_name.slice(0,40)}</div>
        )
        const elementsLevel1 = orderList.slice(1, 4).map((one_order, index) =>
            <div key={index} className='pickup-new-block1-sub2-elem'>{one_order.customer_name.slice(0,40)}</div>
        )
        const elementsLevel2 = orderList.slice(4, 13).map((one_order, index) =>
            <div key={index} className='pickup-new-block2-3-sub'>{one_order.customer_name.slice(0,40)}</div>
        )
        return (
            <div>
                <div className='pickup-main-new'>
                    <div className='pickup-background'>
                        <div className='pickup-new-block1'>
                            <div className='pickup-new-block1-sub1'>
                                {elementsLevel0}
                            </div>
                            <div className='pickup-new-block1-sub2'>
                                {elementsLevel1}
                            </div>
                        </div>
                        <div className='pickup-new-right pickup-new-centered-croped-text pickup-new-right-block-2'>
                            {elementsLevel2}
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default Espelho;

