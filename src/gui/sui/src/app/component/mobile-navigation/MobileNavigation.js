import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

import MobileNavigationRenderer from './mobile-navigation-renderer'
import TablePropTypes from '../../../prop-types/TablePropTypes'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'


export default class MobileNavigation extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      items: this.props.navigation[this.props.defaultNavigationIdx] ?
        this.props.navigation[this.props.defaultNavigationIdx].items : null,

      nameItemsGroup: this.props.navigation[this.props.defaultNavigationIdx] ?
        this.props.navigation[this.props.defaultNavigationIdx].text : null,

      groups: this.filterGroupsBySpecialCatalog(
        this.props.navigation[this.props.defaultNavigationIdx] ?
          this.props.navigation[this.props.defaultNavigationIdx].groups : [],

        this.specialCatalogsNames(this.props.staticConfig.specialMenus),
        this.getActiveSpecialCatalogs(this.parseSpecialCatalog(this.props.staticConfig.specialMenus))),
      previousGroup: [],

      previousNavigationIdx: this.props.defaultNavigationIdx
    }

    this.handleOnClick = this.handleOnClick.bind(this)
    this.handleOnBackClick = this.handleOnBackClick.bind(this)
    this.handleBrowserBack = this.handleBrowserBack.bind(this)
  }

  componentDidMount() {
    window.history.pushState({ saleScreen: true }, '', '')
    window.addEventListener('popstate', this.handleBrowserBack)
  }

  componentWillUnmount() {
    window.onpopstate = null
    window.history.replaceState(null, '', '')
  }

  handleBrowserBack(event) {
    if (event) {
      window.history.pushState({ saleScreen: true }, '', '')
      this.handleOnBackClick()
      event.handled = true
    }
  }

  updateNavigationItems(navigationIdx) {
    this.setState({
      items: this.props.navigation[navigationIdx] ?
        this.props.navigation[navigationIdx].items : null,

      nameItemsGroup: this.props.navigation[navigationIdx] ?
        this.props.navigation[navigationIdx].text : null,

      groups: this.filterGroupsBySpecialCatalog(
        this.props.navigation[navigationIdx] ?
          this.props.navigation[navigationIdx].groups : [],

        this.specialCatalogsNames(this.props.staticConfig.specialMenus),
        this.getActiveSpecialCatalogs(this.parseSpecialCatalog(this.props.staticConfig.specialMenus))),

      previousNavigationIdx: navigationIdx,

      previousGroup: []
    })
  }

  render() {
    const { onSellItem, products, staticConfig: { showPrices }, defaultNavigationIdx } = this.props
    const { nameItemsGroup, items, groups, previousGroup, previousNavigationIdx } = this.state
    if (previousNavigationIdx !== defaultNavigationIdx) {
      this.updateNavigationItems(defaultNavigationIdx)
    }
    return (
      <MobileNavigationRenderer
        nameItemsGroup={nameItemsGroup}
        items={this.groupByColumns(items)}
        groups={this.groupByColumns(groups)}
        onClick={this.handleOnClick}
        onBackClick={this.handleOnBackClick}
        showBack={previousGroup.length > 0}
        onSellItem={onSellItem}
        products={showPrices ? products : null}
      />
    )
  }

  handleOnBackClick() {
    const previous = this.state.previousGroup.pop()

    if (previous) {
      this.setState({
        items: previous.items,
        groups: previous.groups,
        nameItemsGroup: previous.nameItemsGroup,
        previousGroup: this.state.previousGroup
      })
    }
  }

  handleOnClick(item) {
    const { items, groups, nameItemsGroup } = this.state

    if (item.product_code != null) {
      return this.props.onSellItem(item)
    }

    const selectedGroup = groups.find(group => group.name === item.name)

    const updatedPrevious = this.state.previousGroup
    updatedPrevious.push({ items, groups, nameItemsGroup })

    this.setState({
      items: selectedGroup.items,
      groups: selectedGroup.groups,
      nameItemsGroup: selectedGroup.text,
      previousGroup: updatedPrevious
    })

    return null
  }

  filterGroupsBySpecialCatalog(groups, specialCatalogsNames, activeSpecialCatalogs) {
    const filteredGroups = []
    groups.forEach(group => {
      if (!specialCatalogsNames[group.name] || activeSpecialCatalogs[group.name]) {
        filteredGroups.push(group)
      }
    })
    return filteredGroups
  }

  getActiveSpecialCatalogs(specialCatalogs) {
    if (specialCatalogs == null) {
      return {}
    }

    const activeSpecialCatalogs = {}
    if (this.props.specialCatalog != null) {
      activeSpecialCatalogs[specialCatalogs[this.props.specialCatalog]] = true
    }

    if (this.props.selectedTable != null && this.props.selectedTable.specialCatalog != null) {
      activeSpecialCatalogs[specialCatalogs[this.props.selectedTable.specialCatalog]] = true
    }

    return activeSpecialCatalogs
  }

  parseSpecialCatalog(specialCatalogs) {
    const ret = {}
    specialCatalogs.forEach(catalog => {
      const parts = catalog.split(':')
      ret[parts[1]] = parts[0]
    })
    return ret
  }

  specialCatalogsNames(specialCatalogs) {
    const ret = {}
    specialCatalogs.forEach(catalog => {
      const parts = catalog.split(':')
      ret[parts[0]] = parts[1]
    })
    return ret
  }

  groupByColumns(items) {
    if (items == null) {
      return []
    }

    const ret = []
    let temp = []
    items.forEach(item => {
      temp.push(item)
      if (temp.length === 2) {
        ret.push(temp)
        temp = []
      }
    })
    if (temp.length > 0) {
      ret.push(temp)
    }
    return ret
  }
}

MobileNavigation.propTypes = {
  navigation: PropTypes.array,
  onSellItem: PropTypes.func,
  staticConfig: StaticConfigPropTypes,
  specialCatalog: PropTypes.string,
  selectedTable: TablePropTypes,
  products: PropTypes.object,
  defaultNavigationIdx: PropTypes.number
}
