import React from 'react';

export default class ChangeStoreStatus extends React.Component {
    render() {
        let storeStatusQuestion = "Tem certeza que deseja fechar a loja?"
        if(this.props.store.status === "Closed") {
            storeStatusQuestion = "Tem certeza que deseja abrir a loja?"
        }
        return (
            <div className="panel panel-danger store-status-panel">
                <div className="panel-heading text-center">
                    <h2>Mudar Status da Loja</h2>
                </div>
                <div className="panel-body text-center">
                    <h2>{storeStatusQuestion}</h2>
                    <div className="container-fluid">
                        <div className="row">
                            <button className="col-xs-offset-3 col-xs-2 btn btn-danger" onClick={this.props.storeStatusChange}>Sim</button>
                            <button className="col-xs-offset-2 col-xs-2 btn btn-primary" onClick={this.props.storeStatusCancel}>Não</button>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}
