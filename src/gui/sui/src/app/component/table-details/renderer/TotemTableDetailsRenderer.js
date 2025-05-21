import { Component } from 'react'
import PropTypes from 'prop-types'

export default class TotemTableDetailsRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return null
  }
}

TotemTableDetailsRenderer.propTypes = {
  tableInfo: PropTypes.shape({
    title: PropTypes.string,
    details: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.string,
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      labelStyle: PropTypes.string,
      icon: PropTypes.string
    }))
  }),
  classes: PropTypes.object
}
