import React, { Component } from 'react'
import PropTypes from 'prop-types'

import FilterListBoxRenderer from './renderer/'
import { isKeyDown, isKeyUp } from '../../util/keyboardHelper'
import { NumPad } from '../dialogs/numpad-dialog'

function getNewFilterList(filterValue, allValues) {
  return allValues.filter(value => {
    return filterValue === '' || value.toString()
      .indexOf(filterValue) >= 0
  })
}


export default class FilterListBox extends Component {
  constructor(props) {
    super(props)

    this.state = {
      filterValue: '',
      visible: true,
      filteredValues: props.allValues,
      chosenValue: props.allValues[0],
      chosenIndex: 0
    }

    this.props.setFilteredValue(this.state.chosenValue)

    this.handleSelectListItem = this.handleSelectListItem.bind(this)
    this.handleInputChange = this.handleInputChange.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
  }

  static getDerivedStateFromProps(props, state) {
    const { allValues } = props
    const { filterValue, chosenIndex } = state

    const filteredValues = getNewFilterList(filterValue, allValues)

    let nextChosenIndex
    let nextChosenValue
    if (allValues.length) {
      nextChosenValue = filteredValues[chosenIndex]
      nextChosenIndex = chosenIndex
    } else {
      nextChosenValue = filteredValues[0]
      nextChosenIndex = 0
    }
    if (state.chosenValue !== nextChosenValue) {
      props.setFilteredValue(nextChosenValue)
    }
    return { filterValue, filteredValues, chosenValue: nextChosenValue, chosenIndex: nextChosenIndex }
  }

  render() {
    const { title, showFilter, direction, scrollY } = this.props
    const { filterValue, filteredValues, chosenValue } = this.state

    return (
      <FilterListBoxRenderer
        title={title}
        list={filteredValues}
        chosenValue={chosenValue}
        showFilter={showFilter}
        onItemSelect={this.handleSelectListItem}
        direction={direction}
        scrollY={scrollY}
      >
        <NumPad
          value={filterValue}
          onTextChange={this.handleInputChange}
          forceFocus={true}
          showDoubleZero={true}
          textAlign="right"
        />
      </FilterListBoxRenderer>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyPressed, false)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyPressed, false)
  }

  handleInputChange = (filterValue) => {
    if (isNaN(filterValue)) {
      return
    }

    const filteredValues = getNewFilterList(filterValue, this.props.allValues)
    const chosenValue = filteredValues[0]
    const chosenIndex = 0

    this.setState({ filterValue, filteredValues, chosenValue, chosenIndex })
    this.props.setFilteredValue(chosenValue)
  }

  handleSelectListItem(chosenIndex) {
    const chosenValue = this.state.filteredValues[chosenIndex]
    this.setState({ chosenValue, chosenIndex })
    this.props.setFilteredValue(chosenValue)
  }

  handleKeyPressed(event) {
    if (isKeyDown(event)) {
      const chosenIndex = this.state.chosenIndex - 1
      if (chosenIndex >= 0) {
        this.handleSelectListItem(chosenIndex)
      }
    } else if (isKeyUp(event)) {
      const chosenIndex = this.state.chosenIndex + 1
      if (chosenIndex <= this.state.filteredValues.length - 1) {
        this.handleSelectListItem(chosenIndex)
      }
    }
  }
}

FilterListBox.propTypes = {
  title: PropTypes.string,
  allValues: PropTypes.array,
  setFilteredValue: PropTypes.func,
  showFilter: PropTypes.bool,
  direction: PropTypes.string,
  scrollY: PropTypes.bool
}
