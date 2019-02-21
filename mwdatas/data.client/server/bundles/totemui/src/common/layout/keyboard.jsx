import React, { Component } from 'react'

export default class keyboard extends Component {
    render() {
        let clas = 'text-center bnt-teclado'
        clas += this.props.className ? ` ${this.props.className}` : ''
        return (
            <div className={clas} onClick={this.props.onClick}>
                <span>{this.props.value}</span>
            </div>
        )
    }
}