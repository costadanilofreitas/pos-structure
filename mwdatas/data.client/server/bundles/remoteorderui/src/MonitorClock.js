import React from 'react';
import DateFormatter from './DateFormatter'

class StoreInfo extends React.Component {
    constructor(props) {
        super(props);

        this.state = {currentDate: new Date()}

        this.setState = this.setState.bind(this);
        this.updateClock = this.updateClock.bind(this);
    }

    updateClock() {
        this.setState({currentDate: new Date()})
    }

    componentDidMount() {
        this.intervalId = setInterval(this.updateClock, 1000)
    }

    componentWillUnmount() {
        clearInterval(this.intervalId)
    }

    render() {
        return (
            <DateFormatter date={this.state.currentDate} format="HH:mm:ss"/>
        );
    }
}

export default StoreInfo;
