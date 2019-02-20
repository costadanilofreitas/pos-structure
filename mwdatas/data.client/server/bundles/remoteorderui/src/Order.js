import React from 'react';
import {OrderItems} from './OrderItems'
import AddressInfo from './AddressInfo'
import * as moment from 'moment'

class Order extends React.Component {
    constructor(props) {
        super(props);

        this.handleOrderClick = this.handleOrderClick.bind(this);
        this.cancelSendingToProduction = this.cancelSendingToProduction.bind(this);
        this.sendOrderToProduction = this.sendOrderToProduction.bind(this);
        this.handleAddressToggle = this.handleAddressToggle.bind(this);

        this.state = {
            sendingToProduction: false,
            showAddress: false
        }
    }

    render() {
        const expensiveOrder = this.props.total > 150.0;
        let orderBodyClass = "order-body ";
        if(this.props.status === "Ok") {
            orderBodyClass += expensiveOrder ? "order-expensive" : "order-success";
        } else if(this.props.status === "Warning") {
            orderBodyClass += "order-warning";
        } else if(this.props.status === "Danger") {
            orderBodyClass += "order-danger";
        } else {
            orderBodyClass += expensiveOrder ? "order-expensive" : "order-not-set";
        }

        let now = moment();

        let formattedPickupTime;
        if(this.props.pickupTime !== undefined) {
            let pickUpTime = moment(this.props.pickupTime);
            formattedPickupTime = this.formatDuration(now, pickUpTime);
        }
        else {
            formattedPickupTime = "-";
        }

        let receiveTime = moment(this.props.receiveTime);
        let formattedReceiveTime = this.formatDuration(receiveTime, now);


        return (
            <div className="order-panel" onClick={this.handleOrderClick}>
                {this.state.sendingToProduction &&
                <div className="order-actions">
                    <div className="order-action-button pull-left bg-danger" onClick={this.sendOrderToProduction}>Produzir</div>
                    <div className="order-action-button pull-left address-button" onClick={this.handleAddressToggle}>Endereço</div>
                    <div className="order-action-button pull-right bg-primary" onClick={this.cancelSendingToProduction}>Fechar</div>
                </div>}
                {this.state.showAddress &&
                <AddressInfo {...this.props}/>}
                <div className="order-header clearfix">
                    <div className="pull-left">[{this.props.id % 1000}]</div>
                    <div className="pull-right">[{this.props.shortReference}]</div>
                    <div className="pull-right">[{this.props.partner}]</div>
                </div>
                <div className={orderBodyClass}>

                    <div className="client-name">{this.props.clientName.length > 28 ? this.props.clientName.substr(0, 28) : this.props.clientName}</div>

                    <OrderItems items={this.props.items} smallSize={this.props.smallSize}/>
                </div>
                <div className="order-footer">
                    <span className="order-time pull-left"><strong>TM:</strong> {formattedPickupTime}</span>
                    <span className="order-time pull-right"><strong>TR:</strong> {formattedReceiveTime}</span>
                </div>
            </div>
        )
    }

    handleAddressToggle(e) {
        this.setState({showAddress: !this.state.showAddress});
        e.stopPropagation();
    }

    sendOrderToProduction() {
        this.props.sendOrderToProduction(this.props);
    }

    handleOrderClick() {
        this.setState({
            sendingToProduction: !this.state.sendingToProduction,
            showAddress: !this.state.sendingToProduction && this.state.showAddress
        });
    }

    cancelSendingToProduction(e) {
        this.setState({
            sendingToProduction: false,
            showAddress: false
        });
        e.stopPropagation();
    }

    zeroFill(value) {
        if(value.length <= 1) {
            return "0" + value;
        } else {
            return value;
        }
    }

    formatDuration(startDate, endDate) {
        let durationInMilis = endDate.valueOf() - startDate.valueOf();
        let formattedDuration = "";
        if(durationInMilis > 0) {
            let duration = moment.duration(durationInMilis);
            let hours = duration.hours();
            let minutes = duration.minutes();
            let seconds = duration.seconds();
            let formattedHours = this.zeroFill("" + hours);
            let formattedMinutes = this.zeroFill("" + minutes);
            let formattedSeconds = this.zeroFill("" + seconds);

            formattedDuration = formattedHours + ":" + formattedMinutes + ":" + formattedSeconds;
        }

        return formattedDuration;
    }
}

export default Order;
