import React, {Component} from 'react'
import _ from 'lodash'
import Espelho from './Espelho'

class App extends Component {
    constructor(props) {
        super(props)
        window.history.pushState(null, null, document.URL);
        this.state = {
            paidOrders: [],
            readyOrders: [],
            pickedOrders: [],
            currentPage: 0,
            currentTab: 0,
            orderTotalTime: null,
            orderReadyTime: null,
            orderPaidTime: null,
            readyOrdersProportion: null
        }
        this.wsUrl = "ws://" + window.location.hostname + ":8282/"
        this.ws = new WebSocket(this.wsUrl);
        this.attempIntervalId = null
        this.receivedCachedOrders = false
        this.paidOrderDuration = 60 // in seconds
        this.readyOrdersTimeout = 60000 // in milli-seconds
        this.clockOffset = 0 // server epoch time offset with server clock
        this.clearPaidOrders = false

        //this.state = {
        //paidOrders: [
        //{ timestamp: '18/09/2017 11:15:05', order_id: '3', customer_name: 'Jerome', origin: 'Loja', order_items: 'Whopper' },
        //{ timestamp: '18/09/2017 11:15:05', order_id: '5', customer_name: 'Gustavo', origin: 'Loja' },
        //{ timestamp: '18/09/2017 11:15:05', order_id: '6', customer_name: 'Alexandre', origin: 'Loja' },
        //],
        //readyOrders: [
        //{ timestamp: '18/09/2017 11:15:05', order_id: '3', customer_name: 'Jerome', origin: 'Loja', order_items: 'Whopper' },
        //{ timestamp: '18/09/2017 11:15:05', order_id: '5', customer_name: 'Gustavo', origin: 'Loja' },
        //{ timestamp: '18/09/2017 11:15:05', order_id: '6', customer_name: 'Alexandre', origin: 'Loja' },
        //],
        //currentTab: 0,
        //}
        this.wsReconnect = this.wsReconnect.bind(this)
        this.increaseTimer = this.increaseTimer.bind(this)
    }

    componentDidMount() {
        this.wsSetup()
        this.timerIntervalId = setInterval(this.increaseTimer, 1000);
    }

    componentWillUnmount() {
        clearInterval(this.timerIntervalId);
        this.ws.close();
    }

    wsSetup() {
        this.ws.onopen = () => this.ws_onOpen()
        this.ws.onmessage = (m) => this.ws_onMessage(m)
        this.ws.onclose = () => this.ws_onClose()
    }

    wsReconnect() {
        this.receivedCachedOrders = false
        this.ws = new WebSocket(this.wsUrl)
        this.wsSetup()
    }

    ws_onOpen() {
        if (this.attempIntervalId) {
            clearInterval(this.attempIntervalId);
        }
    }

    ws_onClose() {
        setTimeout(this.wsReconnect, 4000);
    }

    ws_onMessage(rec_data) {
        if (typeof rec_data.data === "string") {
            if (rec_data.data.length > 0) {
                try {
                    const rec_data_json = JSON.parse(rec_data.data)
                    if (rec_data_json.params !== 'undefined') {
                        this.setState({
                            orderTotalTime: rec_data_json.params.total_time_mean || null,
                            orderReadyTime: rec_data_json.params.ready_time_mean || null,
                            orderPaidTime: rec_data_json.params.paid_time_mean || null,
                            readyOrdersProportion: rec_data_json.params.ready_orders_proportion || null,
                        })
                        if (rec_data_json.msg_type === 'CACHED_ORDERS') {
                            if (!this.receivedCachedOrders) {
                                const pickedOrders = rec_data_json.params.orders_picked
                                this.clockOffset = (Date.now() / 1000) - (rec_data_json.params.server_clock)
                                this.receivedCachedOrders = true
                                // let newReadyOrders = rec_data_json.params.orders_to_pick
                                this.readyOrdersTimeout = 1000 * parseInt(rec_data_json.params.display_duration, 10)
                                this.paidOrderDuration = 60 * parseInt(rec_data_json.params.pedido_ativos_duracao, 10)
                                this.couponBlinkTime = parseInt(rec_data_json.params.coupon_blink, 10)
                                this.TMABlinkTime = parseInt(rec_data_json.params.TMA_blink, 10)
                                this.TMONTBlinkTime = parseInt(rec_data_json.params.TMONT_blink, 10)
                                this.TMPDVBlinkTime = parseInt(rec_data_json.params.TMPDV_blink, 10)
                                this.percentageBlinkTime = parseInt(rec_data_json.params.percentage_blink, 10)
                                const newReadyOrders = rec_data_json.params.orders_to_pick.map(one_order => {
                                    const elapsedTime = (Date.now() / 1000) - one_order.timestamp_ready + (this.clockOffset)
                                    one_order.displayCount = Math.max(Math.floor((this.readyOrdersTimeout / 1000) - elapsedTime), 0)
                                    one_order.timer = Math.floor((Date.now() / 1000) - one_order.timestamp + (this.clockOffset))
                                    return one_order
                                })
                                let newPaidOrders = rec_data_json.params.orders_paid.map(one_order => {
                                    one_order.displayCount = Math.floor(this.readyOrdersTimeout / 1000)
                                    one_order.timer = Math.floor((Date.now() / 1000) - one_order.timestamp + (this.clockOffset))
                                    return one_order
                                })

                                this.setState({
                                    paidOrders: newPaidOrders,
                                    readyOrders: newReadyOrders,
                                    pickedOrders: typeof(pickedOrders) !== 'undefined' && pickedOrders !== null ? pickedOrders : this.state.pickedOrders
                                })
                            }
                        } else {
                            let one_custom = rec_data_json.params

                            one_custom.timer = Math.floor((Date.now() / 1000) - rec_data_json.params.timestamp + (this.clockOffset))

                            switch (one_custom.order_state) {
                                case 'PAID':
                                    const paidOrder = this.state.paidOrders.find(e => (e.order_id === one_custom.order_id))
                                    if (!paidOrder) {
                                        this.setState({
                                            paidOrders: [...this.state.paidOrders, one_custom],
                                            readyOrders: this.state.readyOrders.filter(e => e.order_id !== one_custom.order_id)
                                        })
                                    }
                                    break
                                case 'READY_TO_PICK':
                                    let readyOrder = this.state.paidOrders.find(e => (e.order_id === one_custom.order_id))
                                    if (readyOrder) {
                                        readyOrder.countdown = Date.now()
                                        const elapsedTime = (Date.now() / 1000) - rec_data_json.params.timestamp_ready + (this.clockOffset)
                                        readyOrder.displayCount = Math.max(Math.floor((this.readyOrdersTimeout / 1000) - elapsedTime), 0)
                                        const newPaidOrders = this.state.paidOrders.filter(e => (e.order_id !== one_custom.order_id))
                                        let newReadyOrders = [readyOrder, ...this.state.readyOrders]
                                        this.setState({
                                            paidOrders: newPaidOrders,
                                            readyOrders: newReadyOrders,
                                            pickedOrders: this.state.pickedOrders.filter((order) => order.order_id !== one_custom.order_id)
                                        })
                                    } else {
                                        one_custom.countdown = Date.now()
                                        const elapsedTime = (Date.now() / 1000) - one_custom.timestamp_ready + (this.clockOffset)
                                        one_custom.displayCount = Math.max(Math.floor((this.readyOrdersTimeout / 1000) - elapsedTime), 0)
                                        const filterReady = this.state.readyOrders.filter(erd => (erd.order_id !== one_custom.order_id))

                                        const newMap = [one_custom, ...filterReady]

                                        this.setState({
                                            readyOrders: newMap,
                                            pickedOrders: this.state.pickedOrders.filter((order) => order.order_id !== one_custom.order_id)
                                        })
                                    }
                                    break
                                case 'PICKEDUP':
                                    this.setState({
                                        readyOrders: this.state.readyOrders.filter((order) => order.order_id !== one_custom.order_id),
                                        pickedOrders: [one_custom, ...this.state.pickedOrders]
                                    })
                                    break
                                default:
                                    break
                            }
                        }
                    }
                }
                catch (e) {

                }
            }
        }
    }

    increaseTimer() {
        const newPaidOrders = this.state.paidOrders.reduce((accum, one_order) => {
            if ((one_order.displayCount !== 'undefined') && (one_order.displayCount > 0)) {
                one_order.displayCount = Math.max(one_order.displayCount - 1, 0)
            }
            if (one_order.timer < this.paidOrderDuration) {
                one_order.timer = one_order.timer + 1
                accum.push(one_order)
            } else {
                this.clearPaidOrders = true
            }
            return accum
        }, [])

        const removedPaidOrders = this.state.paidOrders.filter(e => (e.timer >= this.paidOrderDuration))
        if (removedPaidOrders.length) {
            const removed_msg = {
                'order_state': 'REMOVED_PAID_LIST',
                'removed_orders': removedPaidOrders,
            }
            this.ws.send(JSON.stringify(removed_msg))
        }

        const incrReadyOrders = this.state.readyOrders.map(order_ready => {
            if (order_ready.timer < 3599) {
                order_ready.timer = order_ready.timer + 1
            }
            if ((order_ready.displayCount !== 'undefined') && (order_ready.displayCount > 0)) {
                order_ready.displayCount = Math.max(order_ready.displayCount - 1, 0)
            }
            return order_ready
        })
        const newReadyOrders = incrReadyOrders.filter(e => (e.displayCount > 0 && e.order_id))
        const removedOrders = incrReadyOrders.filter(e => (e.displayCount === 0 && e.order_id))
        if (removedOrders.length) {
            const removed_msg = {
                'order_state': 'PICKEDUP_LIST',
                'pickedup_orders': removedOrders,
            }
            this.ws.send(JSON.stringify(removed_msg))
        }

        if (this.clearPaidOrders || (newPaidOrders.length > 0) || (newReadyOrders.length > 0) || (removedOrders.length > 0)) {
            this.setState({
                paidOrders: newPaidOrders,
                readyOrders: newReadyOrders
            })
        }

        const newPickedOrders = [...removedOrders, ...this.state.pickedOrders].filter(e => (e.timestamp_ready + 30 * 60) > (new Date() / 1000))
        this.setState({
            pickedOrders: newPickedOrders
        })
        this.clearPaidOrders = false
    }

    changeTab(index) {
        this.setState({currentTab: index, currentPage: 0})
    }

    setOrderReady(order_id) {
        let readyOrder = this.state.paidOrders.find(e => (e.order_id === order_id))
        if (!readyOrder) {
            readyOrder = this.state.pickedOrders.find(e => (e.order_id === order_id))
        }
        readyOrder.order_state = 'READY_TO_PICK'
        readyOrder.countdown = Date.now()
        readyOrder.displayCount = this.readyOrdersTimeout / 1000
        // const newpaidOrders = this.state.paidOrders.filter(e => (e.order_id !== order_id))
        this.setState({
            paidOrders: this.state.paidOrders.filter(e => e.order_id !== order_id),
            pickedOrders: this.state.pickedOrders.filter(e => e.order_id !== order_id)
        })
        this.ws.send(JSON.stringify(readyOrder));
        this.checkActivePage()
    }

    setOrderReturnToPaid(order_id) {
        let paidOrder = this.state.readyOrders.find(e => (e.order_id === order_id))
        paidOrder.order_state = 'PAID'

        this.setState({
            readyOrders: this.state.readyOrders.filter(e => e.order_id !== order_id)
        })
        this.ws.send(JSON.stringify(paidOrder));
        this.checkActivePage()
    }

    setOrderPickedUp(order_id) {
        const pickedupOrder = this.state.readyOrders.find(e => (e.order_id === order_id))
        if (pickedupOrder !== undefined) {
            pickedupOrder.order_state = 'PICKEDUP'
            this.setState({
                readyOrders: this.state.readyOrders.filter(e => e.order_id !== order_id)
            })
            this.ws.send(JSON.stringify(pickedupOrder));
        }
        this.checkActivePage()
    }

    popStageHandler() {
        window.history.pushState(null, null, document.URL);
    }

    secondToStringMMSS(qsec) {
        let mm = Math.floor(qsec / 60)
        let rsec = Math.floor(qsec - (mm * 60))
        if (rsec >= 60) {
            rsec -= 60
            mm += 1
        }
        return (mm < 0) ? "00:00" : (mm < 10 ? '0' + mm.toString() : mm.toString()) + ':' + (rsec < 10 ? '0' + rsec.toString() : rsec.toString())
    }

    calcPages() {
        const MAX_LINES_IN_PAGE = 3;
        const MAX_LINE_SIZE = this.state.currentTab === 0 ? 6 : 4;
        const itemSize = (item) => item.qty_columns //+ (item.qty_columns === 1 ? 0.5 : 0)
        const lineSize = (line) => _.reduce(line, (acc, item) => acc + itemSize(item), 0)

        const orders = ((this.state.currentTab === 0) ? this.state.paidOrders : this.state.readyOrders)
            .sort((a, b) => b.timer - a.timer)
        let pages = []
        let currentPage = []
        let currentLine = []
        for (let order of orders) {
            const currentLineSize = lineSize(currentLine)
            if (currentLineSize > 0 && currentLineSize + itemSize(order) > MAX_LINE_SIZE) {
                currentPage.push([...currentLine])
                currentLine.length = 0
            }
            if (currentPage.length === MAX_LINES_IN_PAGE) {
                pages.push([...currentPage])
                currentPage.length = 0
            }
            currentLine.push(order)
        }
        currentPage.push(currentLine)
        pages.push(currentPage)
        return pages
    }

    getPageOrders() {
        const pages = this.calcPages()
        return _.flattenDeep(pages[this.state.currentPage])
    }

    getNumPages() {
        return this.calcPages().length
    }

    checkActivePage() {
        const pagesLength = this.calcPages().length
        if (this.state.currentPage > 0 && this.state.currentPage >= pagesLength) {
            this.setState({currentPage: pagesLength - 1})
        }
    }

    previousPage() {
        this.setState({currentPage: _.max([0, this.state.currentPage - 1])})
    }

    nextPage() {
        this.setState({currentPage: _.min([this.getNumPages() - 1, this.state.currentPage + 1])})
    }

    renderPickedHistory() {
        const now = (Date.now() / 1000) + this.clockOffset
        return this.state.pickedOrders.filter(order => {
            return (now - order.timestamp_ready) < (30 * 60)
        }).map(order => {
            return (
                <div className='historico-item' key={order.order_id}>
                    <div>
                        <span className='pedido'>{`Pedido: ${order.order_id}`}</span>
                        {order.customer_name && order.customer_name !== order.order_id && <span className='nome'>{`Cliente: ${order.customer_name}`}</span>}
                        <div style={{clear: 'both'}}/>
                    </div>
                    <div
                        className='pickup-order-cel-lev1-button-ready pickup-button-ready-return'
                        style={{marginLeft: 'auto', marginRight: 'auto'}}
                        onClick={() => this.setOrderReady(order.order_id)}
                    />
                </div>
            )
        })
    }
    render() {
        const order_list_class = 'pickup-order-cel-lev1 ' + (this.state.currentTab === 0 ? 'pickup-order-cel-lev1-paid' : 'pickup-order-cel-lev1-ready')
        const timeToBlinking = this.TMABlinkTime

        let ordersList = this.getPageOrders()
        if (this.state.currentTab === 1) {
            ordersList = ordersList.sort((a, b) => b.displayCount - a.displayCount)
        }

        const ordersPaidReady = ordersList.map((one_order, index) =>
            <div key={index} className='pickup-order-cont' onClick={() => this[this.state.currentTab === 0 ? 'setOrderReady' : 'setOrderPickedUp'](one_order.order_id)}>
                <div className='pickup-order-cont-sub'>
                    <div className={'pickup-order-cel pickup-order-cel-' + one_order.qty_columns}>
                        <div className={'pickup-order-cel-sub pickup-order-cont-sub-' + one_order.qty_columns}>
                            <div className='pickup-order-cel-title'>
                                <div className={(one_order.timer > timeToBlinking && this.state.currentTab === 0) ? 'pickup-box-time pickup-box-time-blinking' : 'pickup-box-time'}>
                                    <div className="pickup-clock-image"></div>
                                    <div className='pickup-order-cel-lev1-clock'>
                                        {this.state.currentTab === 0 && this.secondToStringMMSS(one_order.timer)}
                                        {this.state.currentTab === 1 && this.secondToStringMMSS(one_order.displayCount)}
                                        {(one_order.sale_type_descr !== "") && <span className={`sale-type ${one_order.sale_type_descr.toLowerCase()}`}>{` ${one_order.sale_type_descr} `}</span>}
                                    </div>
                                </div>
                            </div>
                            <div className={order_list_class + ' box-width-column-' + one_order.qty_columns}>
                                <div className='pickup-order-cel-lev1-content'>
                                    {"\u00A0\u00A0"}Cliente: {one_order.customer_name}

                                    <div className={"block-grid grid-size-" + one_order.qty_columns}>
                                        {one_order.order_sum.split('\n').map((item, key) => {
                                            if (item !== "") {
                                                if (item.toLowerCase().search('sem ') === -1) {
                                                    if (item.toLowerCase().search(' extra ') !== -1) {
                                                        return <div className="block-items" style={{color: 'green', fontWeight: 'bold', textTransform: 'uppercase', fontSize: '1.6vh'}} key={key}>{item}<br/></div>
                                                    }
                                                    return <div className="block-items" key={key}>{item}<br/></div>
                                                } else {
                                                    return <div className="block-items" style={{color: 'red', fontWeight: 'bold', textTransform: 'uppercase', fontSize: '1.6vh'}} key={key}>{item}<br/></div>
                                                }
                                            } else {
                                                return <br key={key}/>
                                            }
                                        })}
                                    </div>

                                </div>
                                {this.state.currentTab === 1 &&
                                <div className='pickup-order-cel-lev1-footer pickup-order-cel-lev2-footer'>
                                    <div className='pickup-order-cel-lev1-button-ready pickup-button-ready-return' onClick={(e) => {
                                             e.stopPropagation()
                                             this.setOrderReturnToPaid(one_order.order_id)
                                         }}/>
                                </div>
                                }
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
        const espelhoScreen = this.state.currentTab === 2
        const tab_list = ['Pedidos Ativos', 'Pedidos Prontos', 'Espelho']
        const tab_div = tab_list.map((one_tab, index) =>
            <div key={index} className={('pickup-tab ' + (this.state.currentTab === index ? 'pickup-tab-selected' : ''))} onClick={() => {this.changeTab(index)}}>{one_tab}</div>
        )
        const shouldBlinkTma = this.state.orderTotalTime > this.TMABlinkTime
        const shouldBlinkPdv = this.state.orderPaidTime > this.TMPDVBlinkTime
        const shouldBlinkMont = this.state.orderReadyTime > this.TMONTBlinkTime

        return (
            <div>
                <div className='pickup-main'>
                    <div className='pickup-header'>
                        <div className='pickup-header-cont'>
                            {tab_div}
                        </div>
                    </div>
                    <div className='pickup-content'>
                        {!espelhoScreen &&
                        <div>
                            <div className='pickup-content-header'>
                                    <span className='campo-tma'>
                                        <span className='metrics-label'>TMA</span>
                                        {this.state.orderTotalTime !== null ?
                                            <span className={shouldBlinkTma ? 'pickup-box-time-blinking' : ''}>{this.state.orderTotalTime ? this.secondToStringMMSS(this.state.orderTotalTime) : '--:--'}</span>
                                            :
                                            <span>--:--</span>
                                        }
                                        <span className='goal'>{`Meta: ${this.TMABlinkTime ? this.secondToStringMMSS(this.TMABlinkTime) : '--:--'}`}</span>
                                    </span>
                                <span className='subcampos'>
                                        <span className='campo-pdv'>
                                            <span className='metrics-label'>PDV: </span>
                                            {this.state.orderPaidTime !== null ?
                                                <span className={shouldBlinkPdv ? 'pickup-box-time-blinking' : ''}>{this.state.orderPaidTime ? this.secondToStringMMSS(this.state.orderPaidTime) : '--:--'}</span>
                                                :
                                                <span>--:--</span>
                                            }|<span className='goal'>{`Meta: ${this.TMPDVBlinkTime ? this.secondToStringMMSS(this.TMPDVBlinkTime) : '--:--'}`}</span>
                                        </span>
                                        <span className='campo-mont'>
                                            <span className='metrics-label'>MONT: </span>
                                            {this.state.orderReadyTime !== null ?
                                                <span className={shouldBlinkMont ? 'pickup-box-time-blinking' : ''}>{this.state.orderReadyTime ? this.secondToStringMMSS(this.state.orderReadyTime) : '--:--'}</span>
                                                :
                                                <span>--:--</span>
                                            }|<span className='goal'>{`Meta: ${this.TMONTBlinkTime ? this.secondToStringMMSS(this.TMONTBlinkTime) : '--:--'}`}</span>
                                        </span>
                                    </span>
                                <span className='campo-pp'>
                                        <span className='metrics-label'>% Leitura</span>
                                    {this.state.readyOrdersProportion !== null ?
                                        <span>{`${(this.state.readyOrdersProportion * 100).toFixed(0)}%`}</span>
                                        :
                                        <span>--%</span>
                                    }
                                    </span>
                                <span className='pages' style={this.state.currentTab === 1 ? {right: '268px'} : {}}>
                                        <span className='page-indicator'>
                                            <span className='metrics-label'>Pág.</span>
                                            <span>{`${this.state.currentPage + 1}/${this.getNumPages()}`}</span>
                                        </span>
                                        <span className='page-button' onClick={() => this.previousPage()}><i className='arrow up'/></span>
                                        <span className='page-button' onClick={() => this.nextPage()}><i className='arrow down'/></span>
                                    </span>
                            </div>
                            <div className='pickup-orders' style={this.state.currentTab === 1 ? {width: '73%'} : {}}>
                                {(this.state.paidOrders[0] && this.secondToStringMMSS(this.state.paidOrders[0].timer) === "00:00") ? "" : ordersPaidReady}
                            </div>
                            {this.state.currentTab === 1 &&
                            <div className='historico'>
                                <div>Histórico de Pedidos</div>
                                <div>Últimos 30 min.</div>
                                <div className='historico-conteudo'>
                                    {this.renderPickedHistory()}
                                </div>
                            </div>
                            }
                        </div>
                        }
                        {espelhoScreen &&
                        <Espelho pickupList={this.state.readyOrders}/>
                        }
                    </div>
                </div>
            </div>
        );
    }
}

export default App;
