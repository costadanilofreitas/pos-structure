import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'
import _ from 'lodash'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'

import { IconStyle } from '../../../constants/commonStyles'
import ActionButton from '../../action-button'
import { isEnter, isEsc } from '../../../util/keyboardHelper'
import Label from '../../label'
import NumpadDialog from '../numpad-dialog'
import StaticConfigPropTypes from '../../../prop-types/StaticConfigPropTypes'

import { BordereauItemInfoCheckBox, BordereauValue } from './StyledBordereauDialog'

const styles = (theme) => ({
  bordereauBackground: {
    position: 'absolute',
    backgroundColor: theme.modalOverlayBackground,
    top: '0',
    left: '0',
    height: '100%',
    width: '100%',
    zIndex: '4',
    alignItems: 'center',
    justifyContent: 'center'
  },
  bordereauBox: {
    position: 'relative',
    top: 'calc(100% / 12)',
    height: 'calc(100% / 12 * 10)',
    background: 'white',
    display: 'flex',
    flexDirection: 'column',
    '@media (max-width: 720px)': {
      width: '100%',
      minHeight: 'calc(100% / 12 * 4)',
      left: '0'
    }
  },
  bordereauTitle: {
    display: 'flex',
    flexDirection: 'column',
    fontSize: '3.0vmin',
    fontWeight: 'bold',
    textAlign: 'center',
    justifyContent: 'center',
    minHeight: '100%',
    color: theme.pressedColor,
    backgroundColor: theme.pressedBackgroundColor
  },
  bordereauItem: {
    width: 'calc(100% / 3)',
    height: 'calc(100% / 8)'
  },
  bordereauItemInfo: {
    fontSize: '2.5vmin',
    display: 'flex',
    alignItems: 'center',
    '@media (max-width: 720px)': {
      fontSize: '2vmin'
    }
  },
  bordereauItemInfoSelected: {
    color: theme.pressedBackgroundColor
  },
  bordereauButtonContainer: {
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
  },
  bordereauButton: {
    display: 'flex',
    flexDirection: 'row'
  }
})


class BordereauDialog extends Component {
  constructor(props) {
    super(props)
    const availableSaleTypes = this.props.staticConfig.availableSaleTypes
    const allSaleTypes = []
    _.forEach(availableSaleTypes, function (x) {
      _.forEach(x, function (y) {
        allSaleTypes.push(y)
      })
    })
    this.visibleElement = null
    this.scrollPanel = null
    this.message = (this.props.message || '')
    const hasDelivery = allSaleTypes.includes('DELIVERY')
    const confirmDialog = (this.message === 'confirmDialog')

    this.filteredTenderTypes = props.staticConfig.tenderTypes.filter(function (tender) {
      const notElectronicPayment = tender.electronicTypeId === 0
      return !tender.hasChild && (tender.showInFC || (hasDelivery && !confirmDialog)) && notElectronicPayment
    })

    const values = this.filteredTenderTypes.map((tender) => ({ tenderId: tender.id, amount: 0 }))
    const checkBoxValues = this.filteredTenderTypes.map(() => false)

    this.state = {
      visible: true,
      values: values,
      checkBoxValues: checkBoxValues,
      showNumPad: false,
      currentNumPadValue: 0,
      currentValuesIndex: -1,
      blinkIndex: -1
    }

    this.renderBordereau = this.renderBordereau.bind(this)
    this.handleKeyPressed = this.handleKeyPressed.bind(this)
    this.handleOnOk = this.handleOnOk.bind(this)
    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleGetValue = this.handleGetValue.bind(this)
    this.handleCheckBox = this.handleCheckBox.bind(this)
    this.handleOnTitleClick = this.handleOnTitleClick.bind(this)
    this.getElementDescription = this.getElementDescription.bind(this)
  }

  render() {
    const { visible, showNumPad, currentNumPadValue } = this.state
    const { classes, mobile } = this.props

    if (!visible) {
      return null
    }

    return (
      <div className={classes.bordereauBackground}>
        <div className={classes.bordereauBox} style={{ width: mobile ? '100%' : 'calc(100% / 12 * 10)', left: mobile ? 'none' : 'calc(100% / 12)' }}>
          <div className={'absoluteWrapper'}>
            <FlexGrid direction={'column'}>
              <FlexChild>
                <div
                  className={`${classes.bordereauTitle} test_BordereauDialog_TITLE`}
                  onDoubleClick={this.handleOnTitleClick}
                >
                  <I18N id={this.props.title}/>
                </div>
              </FlexChild>
              {this.renderBordereau()}
              <FlexChild>
                <FlexGrid>
                  <FlexChild outerClassName={classes.bordereauButtonContainer}>
                    <ActionButton
                      onClick={this.handleOnCancel}
                      className={`test_BordereauDialog_CANCEL ${classes.bordereauButton}`}
                    >
                      <div>
                        <IconStyle className="fa fa-ban fa-2x" aria-hidden="true" dialog={true}/>
                      </div>
                      <I18N id="$CANCEL"/>
                    </ActionButton>
                  </FlexChild>
                  <FlexChild outerClassName={classes.bordereauButtonContainer}>
                    <ActionButton
                      onClick={this.handleOnOk}
                      className={`test_BordereauDialog_OK ${classes.bordereauButton}`}
                    >
                      <div>
                        <IconStyle className="fa fa-check fa-2x" aria-hidden="true" dialog={true}/>
                      </div>
                      <I18N id="$OK"/>
                    </ActionButton>
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
            </FlexGrid>
          </div>
        </div>
        {showNumPad &&
          <NumpadDialog
            mask={'currency'}
            default={currentNumPadValue}
            onDialogClose={this.handleOnOk}
            title={'$ENTER_AMOUNT'}
          />
        }
      </div>
    )
  }

  renderBordereau() {
    const { values, checkBoxValues, blinkIndex } = this.state
    const { classes, mobile } = this.props

    const columns = mobile ? 2 : 3
    const maxRows = 6
    let rows = values.length % 3 === 0 ? values.length / 3 : (values.length / 3) + 1
    if (rows > maxRows) {
      rows = maxRows
    }

    const scrollStyle = !mobile ? { display: 'flex', flexWrap: 'wrap', height: '96%', width: '96%', padding: '2%' }
      : { display: 'flex', flexWrap: 'wrap', height: '96%', width: '96%', padding: '2%', overflowY: 'auto' }

    return (
      <FlexChild size={8}>
        <FlexGrid direction={'row'}>
          <ScrollPanel styleCont={scrollStyle} reference={(el) => (this.scrollPanel = el)}>
            {
              this.filteredTenderTypes.map((tender, i) => {
                const ref = (el) => {
                  if (blinkIndex === i) {
                    this.visibleElement = el
                  }
                }
                return (
                  <BordereauValue
                    key={tender.id}
                    ref={ref}
                    columns={columns}
                    rows={rows}
                    blink={blinkIndex === i}
                  >
                    <FlexGrid direction={'row'}>
                      <FlexChild size={mobile ? 2 : 1} innerClassName={classes.bordereauItemInfo}>
                        <BordereauItemInfoCheckBox onClick={() => this.handleCheckBox(i)}>
                          <i
                            className={checkBoxValues[i]
                              ? `fa fa-check-square ${classes.bordereauItemInfoSelected}`
                              : 'far fa-square'}
                            aria-hidden="true"
                            style={mobile
                              ? { margin: '0.5vh', fontSize: '5vmin' }
                              : { margin: '0.5vh', fontSize: '6vmin' }}
                          />
                        </BordereauItemInfoCheckBox>
                      </FlexChild>
                      <FlexChild
                        size={mobile ? 6 : 4}
                        innerClassName={classes.bordereauItemInfo}
                      >
                        <div onClick={() => this.handleGetValue(i)}>
                          {this.getElementDescription(tender)} <br/>
                          <Label key="orderTotalAmount" text={values[i].amount} style="currency"/>
                        </div>
                      </FlexChild>
                    </FlexGrid>
                  </BordereauValue>
                )
              })
            }
          </ScrollPanel>
        </FlexGrid>
      </FlexChild>
    )
  }

  componentDidUpdate() {
    if (this.scrollPanel != null && this.visibleElement != null) {
      this.scrollPanel.ensureVisible(this.visibleElement)
    }
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyPressed, false)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyPressed, false)
  }

  handleKeyPressed(event) {
    const { showNumPad } = this.state
    if (showNumPad) {
      return
    }

    if (isEnter(event)) {
      this.handleOnOk()
    }

    if (isEsc(event)) {
      this.handleOnCancel()
    }
  }

  handleOnOk(value) {
    const { showNumPad, values, currentValuesIndex, checkBoxValues } = this.state
    if (showNumPad) {
      const currentValues = values
      currentValues[currentValuesIndex].amount = value
      this.setState({ showNumPad: false, values: currentValues })
    } else {
      for (let i = 0; i < checkBoxValues.length; i++) {
        if (!checkBoxValues[i] && this.message !== 'confirmDialog') {
          this.setState({ blinkIndex: i })
          setTimeout(() => {
            this.setState({ blinkIndex: -1 })
          }, 3000)

          return
        }
      }

      this.props.closeDialog(JSON.stringify(values))
      this.setState({ visible: false })
    }
  }

  handleOnCancel() {
    const { showNumPad } = this.state
    if (showNumPad) {
      this.setState({ showNumPad: false })
    } else {
      this.props.closeDialog(-1)
      this.setState({ visible: false })
    }
  }

  handleGetValue(index) {
    this.setState({ showNumPad: true, currentNumPadValue: 0, currentValuesIndex: index })
  }

  handleCheckBox(index) {
    const { checkBoxValues } = this.state
    const currentCheckBoxValues = checkBoxValues
    currentCheckBoxValues[index] = !currentCheckBoxValues[index]
    this.setState({ checkBoxValues: currentCheckBoxValues })
  }

  handleOnTitleClick() {
    const { checkBoxValues } = this.state

    const currentCheckBoxValues = []
    for (let i = 0; i < checkBoxValues.length; i++) {
      currentCheckBoxValues.push(true)
    }

    this.setState({ checkBoxValues: currentCheckBoxValues })
  }

  getElementDescription(tender) {
    let parentTender = null
    if (tender.parentId != null) {
      parentTender = this.props.staticConfig.tenderTypes.find(function (element) {
        return element.id === tender.parentId
      })
    }

    return parentTender == null ? tender.descr : `${parentTender.descr} ${tender.descr}`
  }
}

BordereauDialog.propTypes = {
  classes: PropTypes.object,
  title: PropTypes.string,
  mobile: PropTypes.bool,
  staticConfig: StaticConfigPropTypes,
  message: PropTypes.string,
  closeDialog: PropTypes.func
}

export default injectSheet(styles)(BordereauDialog)
