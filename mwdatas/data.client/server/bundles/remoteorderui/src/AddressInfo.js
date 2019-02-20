import React from 'react';

class AddressInfo extends React.Component {
    render() {
        return (
            <table className="address-info">
                <col width="110"/>
                <col width="relative_length"/>
                <tr>
                    <td className="address-label">Endereço:............................</td><td className="address-data">{this.props.address}</td>
                </tr>
                {this.props.complement &&
                    <tr>
                        <td className="address-label">Complemento:............................</td><td className="address-data">{this.props.complement}</td>
                    </tr>
                }
                {this.props.reference &&
                    <tr>
                        <td className="address-label">Referência:............................</td><td className="address-data">{this.props.reference}</td>
                    </tr>
                }
                <tr>
                    <td className="address-label">Bairro:........................................................</td><td className="address-data">{this.props.neighborhood}</td>
                </tr>
                <tr>
                    <td className="address-label">CEP:........................................................</td><td className="address-data">{this.props.postal}</td>
                </tr>
                <tr>
                    <td className="address-label">Cidade:........................................................</td><td className="address-data">{this.props.city}</td>
                </tr>
                <tr>
                    <td className="address-label">Estado:........................................................</td><td className="address-data">{this.props.state}</td>
                </tr>
            </table>
        )
    }
}

export default AddressInfo;
