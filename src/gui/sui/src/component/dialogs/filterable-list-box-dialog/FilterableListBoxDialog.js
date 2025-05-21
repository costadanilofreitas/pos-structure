import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'

import { IconStyle } from '../../../constants/commonStyles'
import FilterListBox from '../../filter-listbox'
import { isEsc, isEnter } from '../../../util/keyboardHelper'

const styles = (theme) => ({
  filterableListBoxBackground: {
    position: 'absolute',
    backgroundColor: theme.modalOverlayBackground,
    top: '0',
    left: '0',
    height: '100%',
    width: '100%',
    zIndex: '5',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  filterableListBoxButtons: {
    flex: '1',
    display: 'flex',
    position: 'relative'
  },
  filterableListBoxContent: {
    flex: '6',
    display: 'flex',
    position: 'relative'
  },
  filterableListBox: {
    position: 'relative',
    width: '70%',
    height: 'calc(100% / 12 * 7)',
    background: 'white',
    display: 'flex',
    flexDirection: 'column',
    '@media (max-width: 720px)': {
      width: '100%'
    }
  },
  filterableListBoxNoFilter: {
    position: 'relative',
    width: '40%',
    height: 'calc(100% / 12 * 7)',
    background: 'white',
    display: 'flex',
    flexDirection: 'column',
    '@media (max-width: 720px)': {
      width: '100%'
    }
  },
  filterableListBoxButton: {
    flex: '1',
    color: theme.activeColor,
    backgroundColor: theme.activeBackgroundColor,
    border: 'none',
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    textTransform: 'capitalize',
    '&:not(:last-child)': {
      borderRight: 'solid 1px #fff'
    },
    '&:active': {
      color: theme.pressedColor,
      backgroundColor: theme.pressedBackgroundColor
    },
    '&:focus': {
      outline: '0'
    }
  }
})

class FilterableListBoxDialog extends Component {
  constructor(props) {
    super(props)

    this.allValues = this.props.info.split('|')

    this.state = {
      visible: true,
      chosenValue: this.allValues[0]
    }

    this.handleOnOk = this.handleOnOk.bind(this)
    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
  }

  containerWidth(showFilter) {
    const { mobile } = this.props
    if (mobile) {
      return '100%'
    } else if (showFilter) {
      return '70%'
    }
    return '40%'
  }

  render() {
    const { classes, mask, mobile, type, title, message } = this.props
    const { visible } = this.state

    if (!visible) {
      return null
    }

    const isListBox = type.toLowerCase() === 'listbox'
    const showFilter = mask !== 'NOFILTER' && !isListBox
    const filterableListBoxClass = showFilter ? classes.filterableListBox : classes.filterableListBoxNoFilter
    const currentTitle = !isListBox ? title : message

    return (
      <div className={classes.filterableListBoxBackground}>
        <div className={filterableListBoxClass} style={{ width: this.containerWidth(showFilter) }}>
          <div className={classes.filterableListBoxContent}>
            <FilterListBox
              title={currentTitle}
              allValues={this.allValues}
              setFilteredValue={(value) => this.setState({ chosenValue: value })}
              showFilter={showFilter}
              scrollY={mobile === true}
            />
          </div>
          <div className={classes.filterableListBoxButtons}>
            <button
              className={`${classes.filterableListBoxButton} test_FilterableList_CANCEL`}
              onClick={this.handleOnCancel}
            >
              <IconStyle className="fa fa-ban fa-2x" aria-hidden="true" secondaryColor />
              <I18N id="$CANCEL"/>
            </button>
            <button
              className={`${classes.filterableListBoxButton} test_FilterableList_OK`} onClick={() => this.handleOnOk()}
            >
              <IconStyle className="fa fa-check fa-2x" aria-hidden="true" secondaryColor />
              <I18N id="$OK"/>
            </button>
          </div>
        </div>
      </div>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyPressed, false)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyPressed, false)
  }

  handleOnOk() {
    const { chosenValue } = this.state
    const { type } = this.props

    if (chosenValue == null) {
      return
    }

    let selectedValue = this.allValues.indexOf(chosenValue)
    const isListBox = type.toLowerCase() === 'listbox'
    if (isListBox) {
      selectedValue = `0,${selectedValue}`
    }

    this.props.closeDialog(selectedValue)
  }

  handleOnCancel() {
    this.props.closeDialog(-1)
  }

  handleKeyPressed(event) {
    if (isEnter(event)) {
      this.handleOnOk(this.state.chosenValue)
    }

    if (isEsc(event)) {
      this.handleOnCancel()
    }
  }
}

FilterableListBoxDialog.propTypes = {
  classes: PropTypes.object,
  info: PropTypes.string,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  mask: PropTypes.string,
  mobile: PropTypes.bool,
  type: PropTypes.string,
  message: PropTypes.string
}

export default injectSheet(styles)(FilterableListBoxDialog)
