import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { Tabs, Tab } from '../../../../component/tabs'
import NavigationPageRenderer from './JssNavigationPageRenderer'


export default class MobileNavigationRenderer extends Component {
  render() {
    return (
      <Tabs tabSize={1} contentSize={12}>
        {this.renderAllItems()}
      </Tabs>
    )
  }

  renderAllItems() {
    return (
      <Tab label={this.props.nameItemsGroup}>
        <div className={'container'}>
          <NavigationPageRenderer
            groups={this.props.groups}
            items={this.props.items}
            onClick={this.props.onClick}
            onBackClick={this.props.onBackClick}
            showBack={this.props.showBack}
            products={this.props.products}
          />
        </div>
      </Tab>
    )
  }
}

MobileNavigationRenderer.propTypes = {
  nameItemsGroup: PropTypes.string,
  items: PropTypes.array,
  groups: PropTypes.array,
  onBackClick: PropTypes.func,
  showBack: PropTypes.bool,
  onClick: PropTypes.func,
  products: PropTypes.object
}
