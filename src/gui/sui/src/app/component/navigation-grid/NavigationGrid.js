import React, { Component } from 'react'

import NavigationGridRenderer from './navigation-grid-renderer'


export default class NavigationGrid extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <NavigationGridRenderer
        {...this.props}
      />
    )
  }
}
