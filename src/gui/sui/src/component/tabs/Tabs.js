import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

import { FlexChild, FlexGrid } from '3s-widgets'

import { ensureArray } from '../../util/renderUtil'


export default class Tabs extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { activeIndex: props.defaultActiveIndex || 0 }

    this.handleTabClick = this.handleTabClick.bind(this)
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    return {
      ...prevState,
      activeIndex: nextProps.defaultActiveIndex || 0
    }
  }

  handleTabClick(tabIndex) {
    const fixedChildren = this.getFixedChildren()
    if (tabIndex >= fixedChildren.length) {
      return
    }
    if (fixedChildren[tabIndex].props.onClick != null) {
      fixedChildren[tabIndex].props.onClick()
    } else if (tabIndex !== this.state.activeIndex) {
      this.setState({ activeIndex: tabIndex })
    }
  }

  cloneTabElement = (tab, index = 0) => {
    return (
      React.cloneElement(tab, {
        onClick: () => this.handleTabClick(index),
        isActive: index === this.state.activeIndex
      })
    )
  }
  renderChildrenTabs = () => {
    const { children } = this.props

    const childrenTab = ensureArray(children).filter(x => x != null)

    return (
      <FlexGrid>
        {childrenTab.map((child, index) => (
          <FlexChild size={1} key={index}>
            {this.cloneTabElement(child, index)}
          </FlexChild>
        ))}
      </FlexGrid>
    )
  }

  renderActiveTabContent() {
    const { activeIndex } = this.state
    const childrenTab = this.getFixedChildren()
    return childrenTab[activeIndex].props.children
  }

  getFixedChildren() {
    const { children } = this.props
    return ensureArray(children).filter(x => x != null)
  }

  render() {
    return (
      <FlexGrid direction={'column'}>
        <FlexChild size={this.props.tabSize}>{this.renderChildrenTabs()}</FlexChild>
        <FlexChild size={this.props.contentSize}>{this.renderActiveTabContent()}</FlexChild>
      </FlexGrid>
    )
  }
}

Tabs.propTypes = {
  defaultActiveIndex: PropTypes.number,
  children: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  contentSize: PropTypes.number,
  tabSize: PropTypes.number
}
