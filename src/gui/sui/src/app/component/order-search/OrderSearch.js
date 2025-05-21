import PropTypes from 'prop-types'
import React from 'react'
import OrderSearchRenderer from './order-search-renderer'

export default class OrderSearch extends React.Component {
  constructor(props) {
    super(props)
    this.handleOnRendererChange = this.handleOnRendererChange.bind(this)
  }

  handleOnRendererChange(nextState) {
    this.props.onChange({ ...this.props.value, ...nextState })
  }

  render() {
    return <OrderSearchRenderer value={this.props.value} onChange={this.handleOnRendererChange}/>
  }
}

OrderSearch.propTypes = {
  onChange: PropTypes.func,
  value: PropTypes.shape({
    text: PropTypes.string,
    size: PropTypes.number
  })
}
