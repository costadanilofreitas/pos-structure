import React, { Component } from 'react'

export default class grid extends Component {

    toCssClasses(numbers, className) {
        const cols = numbers ? numbers.split(' ') : []
        let classes = ''

        if (cols[0] && cols[0] != 0) classes += `col-xs-${cols[0]}`
        if (cols[1] && cols[1] != 0) classes += ` col-sm-${cols[1]}`
        if (cols[2] && cols[2] != 0) classes += ` col-md-${cols[2]}`
        if (cols[3] && cols[3] != 0) classes += ` col-lg-${cols[3]}`

        classes += className ? ` ${className}` : ''

        return classes
    }

    render() {
        const gridClasses = this.toCssClasses(this.props.cols || '12', this.props.className)
        return (
            <div className={gridClasses} onClick={this.props.onClick} style={this.props.style} >
                {this.props.children}
            </div>
        )
    }
}