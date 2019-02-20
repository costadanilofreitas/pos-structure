import React from 'react';

export default class StoreInfo extends React.Component {
    render() {
        if (this.props.store === null) {
            return (
                <span className="footer-label">Carregando</span>
            )
        } else {
            let storeStatusLabel = "ABERTA";
            if(this.props.store.status === "Closed") {
                storeStatusLabel = "FECHADA";
            }
            else if(this.props.store.status === "Changing") {
                storeStatusLabel = "ATUALIZANDO";
            }
            return (
                <span onClick={this.props.storeLabelClick} className="footer-label">Loja: {this.props.store.id}: {this.props.store.name} - {storeStatusLabel}</span>
            )
        }
    }
}
