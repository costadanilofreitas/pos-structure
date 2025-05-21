import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid, Image } from '3s-widgets'

import Label from '../../../../component/label'
import KeyboardWrapper from '../../../../component/dialogs/keyboard-dialog/keyboard-dialog/KeyboardWrapper'
import RendererChooser from '../../../../component/renderer-chooser'
import { orderInState } from '../../../util/orderValidator'
import OrderState from '../../../model/OrderState'

class BarcodeScreenRenderer extends Component {
  constructor(props) {
    super(props)

    this.handleOnSellClick = this.handleOnSellClick.bind(this)
    this.callback = this.callback.bind(this)

    this.state = {
      typedText: ''
    }
  }

  render() {
    const { classes, selectedLine, order } = this.props

    const keyboardProps = {
      value: this.state.typedText,
      keyboardVisible: false,
      readOnly: true,
      showHideKeyboardButton: false,
      showSellByBarcodeButton: true,
      handleOnInputChange: this.handleOnInputChange,
      flat: true
    }

    const orderInProgress = orderInState(order, OrderState.InProgress)

    return (
      <FlexGrid direction={'column'} className={classes.mainBarcodeContainer}>
        <FlexChild size={1}>
          <FlexGrid direction={'row'}>
            <FlexChild size={9}>
              <RendererChooser
                desktop={<KeyboardWrapper {...keyboardProps}/>}
                mobile={<KeyboardWrapper {...keyboardProps}/>}
                totem={<KeyboardWrapper {...keyboardProps} />}
              />
            </FlexChild>
            <FlexChild size={1} innerClassName={classes.sellByBarcodeButton}>
              <i
                className={'fas fa-shopping-cart fa-2x'}
                aria-hidden="true"
                style={{ margin: '0.5vh' }}
                onClick={this.handleOnSellClick}
              />
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        <FlexChild size={6} innerClassName={classes.barcodeProductDescriptionContainer}>
          <FlexGrid direction={'row'}>
            <FlexChild className={classes.productImage}>
              <Image
                src={[`./images/PRT${selectedLine != null && selectedLine.partCode ? selectedLine.partCode.padStart(8, '0') : ''}.png`]}
                objectFit={'contain'}
              />
            </FlexChild>
            <FlexChild>
              <FlexGrid direction={'column'}>
                <FlexChild>
                  <div className={classes.productDescriptionBox}>
                    <p className={classes.productBoxTitle}>
                      <I18N id={'$PRODUCT_CODE'}/>
                    </p>
                    <p className={classes.productBoxDescription}>
                      {selectedLine != null && orderInProgress
                        ? selectedLine.partCode
                        : '-'
                      }
                    </p>
                  </div>
                </FlexChild>
                <FlexChild>
                  <div className={classes.productDescriptionLastBox}>
                    <p className={classes.productBoxTitle}>
                      <I18N id={'$PRODUCT_DESCRIPTION'}/>
                    </p>
                    <p className={classes.productBoxDescription}>
                      {selectedLine != null && orderInProgress
                        ? selectedLine.productName
                        : '-'
                      }
                    </p>
                  </div>
                </FlexChild>
              </FlexGrid>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        <FlexChild size={3}>
          <FlexGrid>
            <FlexChild>
              <div className={classes.productPriceBox}>
                <p className={classes.productBoxTitle}>
                  <I18N id={'$UNIT_PRICE'}/>
                </p>
                <p className={classes.productBoxDescription}>
                  {selectedLine != null && selectedLine.unitPrice != null && orderInProgress
                    ? <Label key="unitPrice" text={selectedLine.unitPrice} style="currency"/>
                    : '-'
                  }
                </p>
              </div>
            </FlexChild>
            <FlexChild>
              <div className={classes.productPriceBox}>
                <p className={classes.productBoxTitle}>
                  <I18N id={'$QUANTITY'}/>
                </p>
                <p className={classes.productBoxDescription}>
                  {selectedLine != null && orderInProgress
                    ? selectedLine.qty
                    : '-'
                  }
                </p>
              </div>
            </FlexChild>
            <FlexChild>
              <div className={classes.productPriceLastBox}>
                <p className={classes.productBoxTitle}>
                  <I18N id={'$ITEM_TOTAL_VALUE'}/>
                </p>
                <p className={classes.productBoxDescription}>
                  {selectedLine != null && selectedLine.itemPrice != null && orderInProgress
                    ? <Label key="unitPrice" text={selectedLine.itemPrice} style="currency"/>
                    : '-'
                  }
                </p>
              </div>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
      </FlexGrid>
    )
  }

  handleOnInputChange = (typedText) => {
    this.setState({ typedText })
  }

  callback(response) {
    if (response.ok && ['Clear', 'True'].includes(response.data)) {
      this.setState({ typedText: '' })
    }
  }

  handleOnSellClick() {
    this.props.handleOnSellByBarcode(this.state.typedText, null, this.callback)
  }


  handleKeyPressed = (event) => {
    const hasDialog = this.props.dialogs.length !== 0
    if (hasDialog) {
      return
    }

    let typedText = this.state.typedText
    const keyCode = event.keyCode
    if (keyCode === 13) {
      this.props.handleOnSellByBarcode(typedText, null, this.callback)
    } else if (keyCode === 8) {
      typedText = typedText.substring(0, typedText.length - 1)
      this.setState({ typedText })
    } else {
      const validDigit = (keyCode >= 48 && keyCode <= 57) || (keyCode >= 96 && keyCode <= 105)
      if (validDigit) {
        const typedChar = String.fromCharCode((keyCode >= 96 && keyCode <= 105) ? (keyCode - 48) : keyCode)
        typedText += typedChar
        this.setState({ typedText })
      }
    }
  }

  componentDidMount() {
    document.addEventListener('keydown', this.handleKeyPressed, false)
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleKeyPressed, false)
  }
}

BarcodeScreenRenderer.propTypes = {
  classes: PropTypes.object,
  selectedLine: PropTypes.object,
  dialogs: PropTypes.array,
  handleOnSellByBarcode: PropTypes.func,
  order: PropTypes.object
}

export default BarcodeScreenRenderer
