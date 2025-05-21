import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import { IconStyle } from '../../../constants/commonStyles'
import { isEsc, isEnter } from '../../../util/keyboardHelper'
import TableDetails from '../../../app/component/table-details'
import TablePropTypes from '../../../prop-types/TablePropTypes'


const styles = (theme) => ({
  absoluteWrapper: {
    position: 'absolute',
    height: '100%',
    width: '100%'
  },
  tableDetailsBackground: {
    position: 'absolute',
    backgroundColor: theme.modalOverlayBackground,
    top: '0',
    left: '0',
    height: '100%',
    width: '100%',
    zIndex: '4',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  tableDetails: {
    position: 'relative',
    width: '30%',
    height: `calc( (100% + (2 * ${theme.defaultPadding}) ) / 11 * 6)`,
    background: 'white',
    display: 'flex',
    flexDirection: 'column',
    '@media (max-width: 720px)': {
      width: '100%'
    }
  },
  tableDetailsContainer: {
    background: 'white',
    flex: '5',
    position: 'relative'
  },
  tableDetailsButtons: {
    flex: '1',
    display: 'flex',
    position: 'relative'
  },
  tableDetailsButton: {
    flex: '1',
    color: theme.activeColor,
    backgroundColor: theme.activeBackgroundColor,
    border: 'none',
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    textTransform: 'capitalize',
    '&:active': {
      color: theme.pressedColor,
      backgroundColor: theme.pressedBackgroundColor
    },
    '&:focus': {
      outline: '0'
    }
  }
})

class TableDetailsDialog extends Component {
  constructor(props) {
    super(props)

    this.handleOnOk = this.handleOnOk.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
  }

  render() {
    const { classes } = this.props

    return (
      <div className={classes.tableDetailsBackground}>
        <div className={classes.tableDetails}>
          <div className={classes.tableDetailsContainer}>
            <div className={classes.absoluteWrapper} style={{ display: 'flex' }}>
              <div className={classes.absoluteWrapper}>
                <TableDetails selectedTable={this.props.selectedTable} compact={true}/>
              </div>
            </div>
          </div>
          <div className={classes.tableDetailsButtons}>
            <button className={classes.tableDetailsButton} onClick={this.handleOnOk}>
              <IconStyle className="fa fa-check fa-2x" aria-hidden="true" secondaryColor/>
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
    this.props.msgBus.syncAction('deselect_table')
  }

  handleKeyPressed(event) {
    if (isEnter(event)) {
      this.handleOnOk()
    }
    if (isEsc(event)) {
      this.handleOnOk()
    }
  }
}

TableDetailsDialog.propTypes = {
  classes: PropTypes.object,
  selectedTable: TablePropTypes,
  msgBus: PropTypes.shape({
    syncAction: PropTypes.func.isRequired
  }).isRequired
}

export default injectSheet(styles)(TableDetailsDialog)
