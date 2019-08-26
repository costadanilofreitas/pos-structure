import React, { Component } from 'react'
import Websocket from 'react-websocket'
import config from './config/index'

class App extends Component {
    constructor(props) {
        super(props)
        this.state = {
            pickupList: [],
            rightElementIndex: 20,
            rightElementEndIndex: 40,
        }
        this.purgeOrderList = this.purgeOrderList.bind(this)
        this.receivedCachedOrders = false
        this.display_duration = 60000
        this.clockOffset = 0 // server epoch time offset with server clock
    }

    componentDidMount() {
        this.intervalId = setInterval(this.purgeOrderList, 2500);
    }

    componentWillMount() {
    }

    componentWillUnmount() {
        clearInterval(this.intervalId);
    }

    componentDidUpdate() {
        let idx_1 = 4;
        let idx_2 = 4;
        if (typeof this.refs.right_col_1 !== 'undefined'){
            const right_y_parent = this.refs.right_col_1.getBoundingClientRect().top + this.refs.right_col_1.getBoundingClientRect().height
            for (let i = 0; i < this.refs.right_col_1.children.length; i++) {
                const elem = this.refs.right_col_1.children[i]
                if (elem.getBoundingClientRect().top + elem.getBoundingClientRect().height < right_y_parent) {
                    idx_1++
                    idx_2++
                } else {
                    idx_2++
                }
            }
            if (typeof this.refs.right_col_2 !== 'undefined'){
                for (let i = 0; i < this.refs.right_col_2.children.length; i++) {
                    const elem = this.refs.right_col_2.children[i]
                    if (elem.getBoundingClientRect().top + elem.getBoundingClientRect().height < right_y_parent) {
                        idx_2++
                    }
                }
            }
            if ((idx_1 !== this.state.rightElementIndex && idx_1 > 0) || (idx_2 !== this.state.rightElementEndIndex && idx_2 > 0)) {
                this.setState({
                    rightElementIndex: idx_1,
                    rightElementEndIndex: idx_2,
                })
            }
        }
    }
    onClose() {
        this.receivedCachedOrders = false;
    }
    
    onMessage(rec_data) {
      if (typeof rec_data === "string") {
        if (rec_data.length > 0) {
            try {
                const rec_data_json = JSON.parse(rec_data)
                if (rec_data_json.params !== 'undefined'){
                    if (rec_data_json.msg_type === 'CACHED_ORDERS'){
                        if (!this.receivedCachedOrders){
                            this.clockOffset = (rec_data_json.params.server_clock) - (Date.now() / 1000)
                            this.display_duration = 1000*parseInt(rec_data_json.params.display_duration,0)
                            this.receivedCachedOrders = true
                            let newReadyOrders = rec_data_json.params.orders_to_pick.map(one_order => {
                                one_order.customer_name = one_order.customer_name ? one_order.customer_name.slice(0,20) : one_order.customer_name.order_id.slice(0,20)
                                const elapsedTime = (Date.now() / 1000) - one_order.timestamp_ready + (this.clockOffset)
                                one_order.countdown = Math.max(Math.floor((this.display_duration / 1000) - elapsedTime), 0)
                                return one_order
                            })
                            this.setState({
                                pickupList: newReadyOrders,
                            })
                        }
                    } else {
                        let one_custom = rec_data_json.params
                        if (one_custom.order_state === 'READY_TO_PICK'){
                            if (this.state.pickupList.length !== 0){
                                if (this.state.pickupList.filter(x => x.order_id === one_custom.order_id).length === 0){
                                    const cusn = one_custom.customer_name
                                    const elapsedTime = (Date.now() / 1000) - one_custom.timestamp_ready + (this.clockOffset)
                                    one_custom.countdown = Math.max(Math.floor((this.display_duration / 1000) - elapsedTime), 0)
                                    one_custom.customer_name = cusn ? cusn.slice(0,20) : one_custom.order_id.slice(0,20)
                                    let newRIdx = this.state.rightElementIndex
                                    let newREIdx = this.state.rightElementEndIndex
                                    this.setState({
                                        pickupList: [one_custom, ...this.state.pickupList],
                                        rightElementIndex: ++newRIdx,
                                        rightElementEndIndex: ++newREIdx,
                                    })
                                }
                            } else {
                                const cusn = one_custom.customer_name
                                one_custom.customer_name = cusn ? cusn.slice(0,20) : one_custom.order_id.slice(0,20)
                                const elapsedTime = (Date.now() / 1000) - one_custom.timestamp_ready + (this.clockOffset)
                                one_custom.countdown = Math.max(Math.floor((this.display_duration / 1000) - elapsedTime), 0)
                                this.setState({
                                    pickupList: [one_custom, ...this.state.pickupList]
                                })
                            }
                        } else if (one_custom.order_state === 'PAID'){
                                const newPickupList = this.state.pickupList.filter(e => (e.order_id !== one_custom.order_id))
                                this.setState({ pickupList: newPickupList })

                        } else if (one_custom.order_state === 'PICKEDUP'){
                                const newPickupList = this.state.pickupList.filter(e => (e.order_id !== one_custom.order_id))
                                this.setState({ pickupList: newPickupList })
                        }
                    }
                }
            }
            catch (e) {
            }
        }
      }
    }

    purgeOrderList() {
        const newPickupList = this.state.pickupList.filter(e => ((e.countdown > ((Date.now() / 1000) - e.timestamp_ready + (this.clockOffset))) && e.order_id))
        this.setState({ pickupList: newPickupList })
    }
		
    render() {
        const wsUrl = "ws://" + window.location.hostname + ":" + config.wsPort + "/"
        const orderList = this.state.pickupList.sort((a, b) => b.displayCount - a.displayCount);
        let elementsLevel0 = orderList.slice(0,1).map((one_order) =>
            <div className='pickup-new-block1-sub1-elem'>{one_order.customer_name}</div>
        )
        //elementsLevel0 = window.navigator.userAgent
        const elementsLevel1 = orderList.slice(1, 4).map((one_order) =>
            <div className={('pickup-new-block1-sub2-elem')}>{one_order.customer_name}</div>
        )
        const elementsLevel2 = orderList.slice(4, this.state.rightElementIndex).map((one_order, index) =>
            <div className='pickup-new-block2-3-sub' ref={'right_col_1' + index}>{one_order.customer_name}</div>
        )
        return (
            <div>
                <div className='pickup-main-new pickup-container'>
                    <div className='pickup-background'>
                        <div className='pickup-new-block1'>
                            <div className={'pickup-new-block1-sub1'}>
                                {elementsLevel0}
                            </div>
                            <div className={'pickup-new-block1-sub2'}>
                                {elementsLevel1}
                            </div>
                        </div>
                        <div className='pickup-new-right pickup-new-right-block-2' ref='right_col_1'>
                            {elementsLevel2}
                        </div>
                    </div>
                </div>
                <Websocket url={wsUrl}
                  onMessage={this.onMessage.bind(this)}
                  onClose={this.onClose.bind(this)}/>
            </div>
        );
    }
}

export default App;
