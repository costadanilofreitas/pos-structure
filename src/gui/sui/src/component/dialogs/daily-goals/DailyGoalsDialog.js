import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle, PopupStyledButton } from '../../../constants/commonStyles'
import DailyGoals from '../../../app/component/daily-goals'
import { isEsc, isEnter } from '../../../util/keyboardHelper'
import withState from '../../../util/withState'

const styles = (theme) => ({
  messageBackground: {
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
  message: {
    position: 'relative',
    width: '90%',
    height: 'calc(100% / 12 * 11)',
    background: 'white',
    display: 'flex',
    flexDirection: 'column',
    '@media (max-width: 720px)': {
      width: '100%'
    }
  },
  messageTitle: {
    fontSize: '3.0vmin',
    fontWeight: 'bold',
    justifyContent: 'center',
    display: 'flex',
    textAlign: 'center',
    alignItems: 'center',
    color: theme.pressedColor,
    backgroundColor: theme.dialogTitleBackgroundColor
  },
  messageButtons: {
    height: '100%',
    width: '100%'
  }
})

class DailyGoalsDialog extends Component {
  constructor(props) {
    super(props)
    this.handleOnConfirm = this.handleOnConfirm.bind(this)
  }

  render() {
    const { classes, mask, mobile } = this.props
    const operatorId = mask.split('|')[0]
    const showAmountChart = (mask.split('|')[1]).toLowerCase() === 'true'
    const showItemsChart = (mask.split('|')[2]).toLowerCase() === 'true'
    const showOperatorsTable = (mask.split('|')[3]).toLowerCase() === 'true'
    const showAverageTicketChart = (mask.split('|')[4]).toLowerCase() === 'true'

    return (
      <div className={classes.messageBackground}>
        <FlexGrid className={classes.message} direction={'column'} styled={{ width: mobile ? '100%' : '90%' }}>
          <FlexChild innerClassName={classes.messageTitle}>
            <I18N id={'$DAILY_GOALS'}/>
          </FlexChild>
          <FlexChild size={10}>
            <DailyGoals
              showAmountChart={showAmountChart}
              showItemsChart={showItemsChart}
              showOperatorsTable={showOperatorsTable}
              showAverageTicketChart={showAverageTicketChart}
              showSubtitles={true}
              goalsFlexDirection={'column'}
              selectedOperator={operatorId}
            />
          </FlexChild>
          <FlexChild innerClassName={classes.messageButtons}>
            <PopupStyledButton
              active={true}
              flexButton={true}
              className={`${classes.numpadButton} test_DailyGoalsDialog_OK`}
              onClick={this.handleOnConfirm}
            >
              <IconStyle className="fa fa-check fa-2x" aria-hidden="true" secondaryColor={true}/>
              <I18N id="$OK"/>
            </PopupStyledButton>
          </FlexChild>
        </FlexGrid>
      </div>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.onKeyPressed.bind(this))
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.onKeyPressed.bind(this))
  }

  onKeyPressed(event) {
    if (isEsc(event) || isEnter(event)) {
      this.props.closeDialog()
    }
  }

  handleOnConfirm() {
    this.props.closeDialog()
  }
}

DailyGoalsDialog.propTypes = {
  classes: PropTypes.object,
  mobile: PropTypes.bool,
  closeDialog: PropTypes.func,
  mask: PropTypes.string
}

export default injectSheet(styles)(withState(DailyGoalsDialog, 'mobile'))
