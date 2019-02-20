import React, { Component } from 'react';
import axios from 'axios'
import config from './config/index'
import OrderList from './OrderList'
import StoreInfo from './StoreInfo'
import ChatButton  from './ChatButton'
import {Chat} from "./Chat";
import MonitorClock from "./MonitorClock";
import ChangeStoreStatus from './ChangeStoreStatus'
import {calculateColumns as calculateOrderColumns} from './OrderItems';
import {calculateColumns as calculateRetransmitColumns} from './RetransmitItems';
import BlockUi from 'react-block-ui';
import 'react-block-ui/style.css';
import BurgerLoading from './BurgerLoading';

class App extends Component {
    constructor(props) {
        super(props);

        this.state = {
            chatEnabled: false,
            storeStatusEnabled: false,
            numberOfOrder: 0,
            store: null,
            orders: [],
            pages: null,
            currentPage: 0,
            maxPages: 0,
            columnCount: 4,
            rowCount: 2,
            sendingToProduction: false,
            allChatMessages: [],
            unreadChatMessages: [],
            maxMessageId: -1
        };

        this.toggleChat = this.toggleChat.bind(this);
        this.toggleStoreStatus = this.toggleStoreStatus.bind(this);
        this.numberOfOrdersUpdated = this.numberOfOrdersUpdated.bind(this);
        this.storeStatusChange = this.storeStatusChange.bind(this);
        this.retrieveStoreStatus = this.retrieveStoreStatus.bind(this);
        this.calculatePages = this.calculatePages.bind(this);
        this.updateOrderList = this.updateOrderList.bind(this);
        this.sendOrderToProduction = this.sendOrderToProduction.bind(this);
        this.previousPage = this.previousPage.bind(this);
        this.nextPage = this.nextPage.bind(this);
        this.forceUpdateOrderList = this.forceUpdateOrderList.bind(this);
        this.reprintOrder = this.reprintOrder.bind(this);

        this.getLastMessages = this.getLastMessages.bind(this);
        this.getUpdates = this.getUpdates.bind(this);
        this.mergeMessages = this.mergeMessages.bind(this);
    }

    toggleChat() {
        let newChatEnabled = !this.state.chatEnabled;
        let newUnreadChatMessages = this.state.unreadChatMessages;
        if(newChatEnabled === true) {
            newUnreadChatMessages = []
        }
        this.setState({chatEnabled: newChatEnabled, storeStatusEnabled: false, unreadChatMessages: newUnreadChatMessages});
        this.calculatePages(this.state.orders, newChatEnabled);
    }

    toggleStoreStatus() {
        let newStoreStatusEnabled = !this.state.storeStatusEnabled;
        this.setState({chatEnabled: false, storeStatusEnabled: newStoreStatusEnabled});
        this.calculatePages(this.state.orders, newStoreStatusEnabled);
    }

    numberOfOrdersUpdated(numberOfOrders) {
        this.setState({numberOfOrder:numberOfOrders});
    }

    componentDidMount() {
        this.retrieveStoreStatus();
        this.setState({orders: [], loadingOrders: true});
        this.updateOrderList();
        this.getLastMessages();

        this.chatMessagesIntervalId = setInterval(this.getUpdates, 5000);
        this.intervalId = setInterval(this.updateOrderList, 10000);
    }

    componentWillUnmount() {
        clearInterval(this.intervalId);
        clearInterval(this.chatMessagesIntervalId);
    }

    retrieveStoreStatus() {
        axios.get(config.apiBaseUrl + "/store")
            .then(res => {
                this.setState({store: res.data});
            })
            .catch(error => {
                this.setState({store: null});
                setTimeout(this.retrieveStoreStatus, 5000);
            });
    }

    storeStatusChange() {
        let store = this.state.store;
        let currentStatus = store.status;
        store.status = "Changing";
        this.setState({store: store});

        let url = "/store/open";
        if(currentStatus === "Open") {
            url = "/store/close";
        }

        axios.get(config.apiBaseUrl + url)
            .then(res => {
                this.setState({store: res.data, storeStatusEnabled: false});
                this.calculatePages(this.state.orders, false);
            })
            .catch(error => {
                this.setState({storeStatusEnabled: false});
                alert("Erro mudando status da loja");
                this.retrieveStoreStatus();
            });
    }

    forceUpdateOrderList() {
        this.calculatePages([], false);
        this.updateOrderList();
    }

    updateOrderList(force) {
        if(force === true || !this.state.sendingToProduction) {
            let accumulatedOrders;
            axios.get(config.apiBaseUrl + '/orders/retransmits')
            .then(res => {
                console.log(res)
                accumulatedOrders = res.data;
                return axios.get(config.apiBaseUrl + "/orders/inProduction");
            })
            .then(res => {
                accumulatedOrders = [...accumulatedOrders, ...res.data];
                console.log(accumulatedOrders)
                this.calculatePages(accumulatedOrders);
            })
            .catch(error => {
                console.log(error)
                if(force === true) {
                    this.setState({sendingToProduction: false});
                }
                this.setState({orders: [], pages: [], currentPage: 0, orderPage: null, loadingOrders: true});
            });
        }
    }

    calculatePages(orders, small) {
        let maxColumns = this.state.columnCount;
        if(small !== undefined) {
            if(small) {
                maxColumns = 1;
            }
        } else {
            if(this.state.chatEnabled || this.state.storeStatusEnabled) {
                maxColumns = 1;
            }
        }

        let pages = [];
        let rows = [];
        let columns = [];
        rows.push(columns);
        pages.push(rows);
        let rowIndex = 0;
        let columnIndex = 0;
        let pageIndex = 0;
        for(let orderIndex = 0; orderIndex < orders.length; orderIndex++) {
            let orderColumnWidth = (orders[orderIndex].partner.includes('reentrega') ? calculateRetransmitColumns : calculateOrderColumns)(orders[orderIndex]);
            console.log(orderColumnWidth)
            if(columnIndex + orderColumnWidth > maxColumns && columnIndex > 0) {
                columnIndex = 0;
                rowIndex++;
                if(rowIndex >= this.state.rowCount) {
                    pageIndex++;
                    rowIndex = 0;
                    rows = [];
                    pages.push(rows);
                }

                columns = [];
                rows.push(columns);
            }
            columns.push(orders[orderIndex]);

            columnIndex += orderColumnWidth;
            if(columnIndex >= maxColumns) {
                columnIndex = 0;
                rowIndex++;
                if(rowIndex >= this.state.rowCount) {
                    pageIndex++;
                    rowIndex = 0;
                    rows = [];
                    pages.push(rows);
                }

                columns = [];
                rows.push(columns);
            }
        }

        // Caso a última página esteja vazia. Removemos ela
        let lastPage = pages[pages.length - 1];
        if(lastPage.length === 1) {
            let lastRow = lastPage[0];
            if (lastRow.length === 0) {
                pages.pop();
            }
        }

        let maxPages = pages.length;

        let newCurrentPage = this.state.currentPage;
        if(small !== undefined && small) {
            newCurrentPage = 0;
        }

        if(this.state.currentPage > pageIndex) {
            newCurrentPage = maxPages - 1;
        }

        this.setState({orders: orders, currentPage: newCurrentPage, maxPages: maxPages, pages: pages, loadingOrders: false, sendingToProduction: false, unreadMessages: 1})
    }

    sendOrderToProduction(order) {
        this.setState({sendingToProduction: true});
        axios.get(config.apiBaseUrl + "/orders/sendToProduction/" + order.id)
            .then(res => {
                this.updateOrderList(true);
            })
            .catch(error => {
                alert("Erro enviando order para produção.");
                this.updateOrderList(true);
            });
    }

    reprintOrder(order) {
        this.setState({sendingToProduction: true});
        axios.get(config.apiBaseUrl + "/orders/reprint/" + order.id + "/" + order.originatorID)
            .then(res => {
                this.updateOrderList(true);
            })
            .catch(error => {
                alert("Erro ao reimprimir order.");
                this.updateOrderList(true);
            });
    }

    getLastMessages() {
        let that = this;

        this.retrievingMessages = true;
        axios.get(config.apiBaseUrl + "/chat/lastMessages")
            .then(messages => {
                that.mergeMessages(messages.data, false);

                that.retrievingMessages = false;

                this.getUpdates();
            })
            .catch(error => {
                that.retrievingMessages = false;
            });
    }

    getUpdates() {
        let that = this;

        if(this.retrievingMessages) {
            return;
        }

        this.retrievingMessages = true;
        axios.get(config.apiBaseUrl + "/chat/updates/" + this.state.maxMessageId)
            .then(messages => {
                if(messages.data.length > 0) {
                    that.mergeMessages(messages.data, true);

                    if(that.sendingMessage) {
                        that.sendingMessage = false;
                        that.chatInput.value = "";
                        that.chatInput.disabled = false;
                    }
                }

                that.retrievingMessages = false;
            })
            .catch(error => {
                that.retrievingMessages = false;
            });
    }

    mergeMessages(newMessages, addUnread) {
        let newAllChatMessages = this.state.allChatMessages;
        let newUnreadChatMessages = this.state.unreadChatMessages;
        let newMaxMessageId = this.state.maxMessageId;

        for(let i = 0; i < newMessages.length; i++) {
            newAllChatMessages.push(newMessages[i]);
            if(!this.state.chatEnabled && addUnread === true) {
                newUnreadChatMessages.push(newMessages[i]);
            }

            if(newMessages[i].id > newMaxMessageId) {
                newMaxMessageId = newMessages[i].id;
            }
        }

        this.setState({allChatMessages: newAllChatMessages, unreadChatMessages: newUnreadChatMessages, maxMessageId: newMaxMessageId});
    }

    previousPage() {
        let currentPage = this.state.currentPage - 1;

        this.setState({currentPage: currentPage});
    }

    nextPage() {
        let currentPage = this.state.currentPage + 1;

        this.setState({currentPage: currentPage});
    }

    render() {
        let orderContainerClasses = "col-md-12";
        if(this.state.chatEnabled || this.state.storeStatusEnabled) {
            orderContainerClasses = "col-md-3";
        }
        console.log(this.state.pages)
        return (
            <BlockUi tag="div" blocking={this.state.sendingToProduction} loader={<BurgerLoading/>}>
                <div>
                    <div className="container-fluid">
                        <div className="row">
                            {this.state.storeStatusEnabled &&
                            <div className="col-md-9">
                                <ChangeStoreStatus store={this.state.store} storeStatusChange={this.storeStatusChange} storeStatusCancel={this.toggleStoreStatus}/>
                            </div>
                            }
                            <div className={orderContainerClasses}>
                                {this.state.pages !== null && this.state.pages.length > 0 && <OrderList
                                    smallSize={this.state.chatEnabled || this.state.storeStatusEnabled}
                                    page={this.state.pages[this.state.currentPage]}
                                    sendOrderToProduction={this.sendOrderToProduction}
                                    reprintOrder={this.reprintOrder} />}
                            </div>
                            {this.state.chatEnabled &&
                            <div className="col-md-9">
                                <Chat messages={this.state.allChatMessages} getUpdates={this.getUpdates}/>
                            </div>
                            }
                        </div>
                    </div>
                    <div className="footer">
                        <div className="container-fluid">
                            <div className="row">
                                <div className="footer-container-left">
                                    {this.state.loadingOrders && <span
                                        className="footer-icon refresh-icon glyphicon glyphicon-large glyphicon-alert"
                                        onClick={this.forceUpdateOrderList}/>}
                                    {!this.state.loadingOrders && <span
                                        className="footer-icon refresh-icon glyphicon glyphicon-large glyphicon-repeat"
                                        onClick={this.forceUpdateOrderList}/>}
                                    <StoreInfo storeLabelClick={this.toggleStoreStatus} store={this.state.store}/>
                                </div>

                                <div className="footer-container-right">
                                    <ChatButton onClick={this.toggleChat} unreadMessages={this.state.unreadChatMessages.length}/>
                                </div>

                                <div className="footer-container-middle">
                                    <MonitorClock/>
                                    <span className="footer-label">{"\u00A0\u00A0"}Monitor Expedição :: Zoom 4x2 - Pedidos: {this.state.orders !== null ? this.state.orders.length : "-"}</span>
                                    {this.state.currentPage > 0 &&
                                    <span
                                        className="refresh-icon footer-icon glyphicon glyphicon-chevron-left glyphicon-large"
                                        onClick={this.previousPage}/>}
                                    {!this.state.currentPage > 0 && <span className="refresh-icon glyphicon-large"/>}
                                    {this.state.currentPage < this.state.maxPages - 1 &&
                                    <span
                                        className="footer-icon glyphicon glyphicon-chevron-right glyphicon-large"
                                        onClick={this.nextPage}/>}
                                    {this.state.currentPage >= this.state.maxPages - 1 && <span className="glyphicon-large"/>}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </BlockUi>
        );
    }
}

export default App;
