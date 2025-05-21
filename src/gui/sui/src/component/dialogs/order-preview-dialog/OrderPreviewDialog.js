import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'
import axios from 'axios'

import { I18N } from '3s-posui/core'
import { ensureArray, xmlToJson } from '3s-posui/utils'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle, PopupStyledButton } from '../../../constants/commonStyles'
import { isEsc } from '../../../util/keyboardHelper'
import CustomSalePanel from '../../../app/component/custom-sale-panel'
import ScrollPanelListItems from '../common/scroll-panel-list-items'
import DeliveryOrderInfo from '../common/delivery-order-info'
import withState from '../../../util/withState'


const styles = (theme) => ({
  messageBackground: {
    position: 'absolute',
    backgroundColor: theme.modalOverlayBackground,
    top: '0',
    left: '0',
    height: '100%',
    width: '100%',
    zIndex: '4',
    alignItems: 'center',
    justifyContent: 'center',
    display: 'flex'
  },
  message: {
    position: 'relative',
    minHeight: 'calc(100% / 12 * 10)',
    background: 'white',
    display: 'flex',
    flexDirection: 'column'
  },
  messageTitle: {
    flex: '1',
    display: 'flex',
    flexDirection: 'column',
    fontSize: '3.0vmin',
    fontWeight: 'bold',
    textAlign: 'center',
    justifyContent: 'center',
    minHeight: '100%',
    color: theme.pressedColor,
    backgroundColor: theme.dialogTitleBackgroundColor
  },
  centerInput: {
    fontSize: '2.0vmin',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  infoContainer: {
    padding: theme.defaultPadding,
    height: `calc(100% - 2 * ${theme.defaultPadding}) !important`,
    width: `calc(100% - 2 * ${theme.defaultPadding} - 1px) !important`,
    borderRight: '2px solid rgba(204, 204, 204, 1)'
  },
  buttonContainer: {
    backgroundColor: theme.dialogButtonBackgroundColor,
    '&:active': {
      color: theme.pressedColor,
      backgroundColor: theme.pressedDialogButtonBackgroundColor
    },
    '&:focus': {
      outline: 0
    }
  }

})

class OrderPreviewDialog extends Component {
  constructor(props) {
    super(props)

    this.onTheFly = this.props.contents.Orders['@attributes'].onTheFly === 'true'
    if (this.props.contents.Orders.PreviewOrder != null) {
      this.orderList = ensureArray(this.props.contents.Orders.PreviewOrder).map((order) => {
        return {
          key: order['@attributes'].key,
          descr: order['@attributes'].descr,
          content: this.onTheFly ? order['#text'] : order
        }
      })
    }

    this.state = {
      selected: (this.orderList && this.orderList.length > 0) ? 0 : null,
      loadingOrder: false,
      content: (this.orderList && this.orderList.length > 0) > 0 ? this.orderList[0].content : null,
      visible: false
    }

    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleOnPrintDeliveryOrder = this.handleOnPrintDeliveryOrder.bind(this)
    this.handleOnOk = this.handleOnOk.bind(this)
    this.handleOnPicklist = this.handleOnPicklist.bind(this)
    this.handleOnCoupon = this.handleOnCoupon.bind(this)
    this.handleClick = this.handleClick.bind(this)
  }

  shouldComponentUpdate() {
    return (this.state.visible === true)
  }

  render() {
    const { selected, loadingOrder, content, visible } = this.state
    const { classes, title, mobile, btn } = this.props

    if (!visible || this.orderList == null) {
      return null
    }

    const isDeliveryOrder = this.orderList.length === 1 && this.orderList[0].descr.includes('DLV')

    return (
      <div className={classes.messageBackground}>
        <div className={classes.message} style={{ width: mobile ? '100%' : '70%' }}>
          <div className={'absoluteWrapper'}>
            <FlexGrid direction={'column'}>
              <FlexChild size={1}>
                <div className={classes.messageTitle}>
                  <I18N id={title}/>
                </div>
              </FlexChild>
              <FlexChild size={8} innerClassName={classes.centerInput}>
                <FlexGrid direction={'row'}>
                  {(isDeliveryOrder && content) &&
                    <FlexChild size={1} innerClassName={classes.infoContainer}>
                      <DeliveryOrderInfo order={content.Order || content}/>
                    </FlexChild>
                  }
                  {(this.orderList.length !== 1) &&
                    <FlexChild size={1}>
                      <ScrollPanelListItems
                        listItems={this.orderList}
                        selected={selected}
                        handleClick={this.handleClick}
                      />
                    </FlexChild>
                  }
                  <FlexChild size={1}>
                    {selected != null && !loadingOrder && content &&
                      <CustomSalePanel
                        customOrder={content.Order || content}
                        showHoldAndFire={true}
                        showSummaryChange={!isDeliveryOrder}
                        showSummaryDiscount={true}
                      />
                    }
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
              <FlexChild size={1}>
                <FlexGrid>
                  {btn.includes('CANCEL') &&
                    <FlexChild>
                      <PopupStyledButton
                        active={true}
                        borderRight={btn.length > 1}
                        className={'buttonContainer test_OrderPreviewDialog_CLOSE'}
                        onClick={this.handleOnCancel}
                        flexButton
                      >
                        <IconStyle className="fa fa-ban fa-2x" aria-hidden="true" secondaryColor={true}/>
                        <I18N id="$CLOSE"/>
                      </PopupStyledButton>
                    </FlexChild>
                  }
                  {btn.includes('OK') &&
                    <FlexChild>
                      <PopupStyledButton
                        active={true}
                        borderRight={true}
                        className={'buttonContainer test_OrderPreviewDialog_OK'}
                        onClick={this.handleOnOk}
                        flexButton
                      >
                        <IconStyle
                          className="fa fa-check fa-2x"
                          aria-hidden="true"
                          secondaryColor={true}
                        />
                        <I18N id="$OK"/>
                      </PopupStyledButton>
                    </FlexChild>
                  }
                  {btn.includes('PICKLIST') &&
                    <FlexChild>
                      <PopupStyledButton
                        active={true}
                        borderRight={true}
                        onClick={this.handleOnPicklist}
                        flexButton
                      >
                        <IconStyle
                          className="fa fa-file-alt fa-2x"
                          aria-hidden="true"
                          secondaryColor={true}
                        />
                        <I18N id="$PICKLIST"/>
                      </PopupStyledButton>
                    </FlexChild>
                  }
                  {btn.includes('COUPON') &&
                    <FlexChild>
                      <PopupStyledButton
                        active={true}
                        onClick={this.handleOnCoupon}
                        flexButton
                      >
                        <IconStyle
                          className="fa fa-receipt fa-2x"
                          aria-hidden="true"
                          secondaryColor={true}
                        />
                        <I18N id="$COUPON"/>
                      </PopupStyledButton>
                    </FlexChild>
                  }
                  {btn.includes('PRINT_DELIVERY') &&
                    <FlexChild>
                      <PopupStyledButton
                        active={true}
                        flexButton={true}
                        className={'test_OrderPreviewDialog_PRINT'}
                        onClick={this.handleOnPrintDeliveryOrder}
                        flexButton
                      >
                        <IconStyle
                          className="fa fa-receipt fa-2x"
                          aria-hidden="true"
                          secondaryColor={true}
                        />
                        <I18N id="$PRINT_DELIVERY"/>
                      </PopupStyledButton>
                    </FlexChild>
                  }
                </FlexGrid>
              </FlexChild>
            </FlexGrid>
          </div>
        </div>
      </div>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.onKeyPressed.bind(this), false)

    this.handleClick(this.state.selected, this.state.content)
    this.setState({ visible: true })
  }
  componentWillUnmount() {
    document.removeEventListener('keydown', this.onKeyPressed.bind(this), false)
  }

  onKeyPressed(event) {
    if (isEsc(event)) {
      this.handleOnCancel()
    }
  }

  handleClick(idx, content) {
    if (this.onTheFly) {
      this.setState({
        loadingOrder: true,
        content: null,
        selected: idx
      })
      axios.get(content)
        .then((response) => {
          const order = xmlToJson((new DOMParser()).parseFromString(response.data, 'text/xml')).Order
          this.setState({
            loadingOrder: false,
            content: order
          })
        }, (error) => {
          console.error(error)
          this.setState({
            loadingOrder: false,
            content: null
          })
        })
    } else {
      this.setState({
        content,
        selected: idx
      })
    }
  }

  handleOnCancel() {
    this.props.closeDialog(this.props.btn.indexOf('CANCEL').toString())
  }

  handleOnPrintDeliveryOrder() {
    this.props.closeDialog(this.props.btn.indexOf('PRINT_DELIVERY').toString(), this.orderList[this.state.selected].key)
  }

  handleOnOk() {
    this.props.closeDialog(this.props.btn.indexOf('OK').toString(), this.orderList[this.state.selected].key)
  }

  handleOnPicklist() {
    if (this.state.selected == null) {
      return
    }
    this.props.closeDialog(this.props.btn.indexOf('PICKLIST').toString(), this.orderList[this.state.selected].key)
  }

  handleOnCoupon() {
    if (this.state.selected == null) {
      return
    }
    this.props.closeDialog(this.props.btn.indexOf('COUPON').toString(), this.orderList[this.state.selected].key)
  }
}

OrderPreviewDialog.propTypes = {
  classes: PropTypes.object,
  mobile: PropTypes.bool,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  message: PropTypes.string,
  contents: PropTypes.shape({
    Orders: PropTypes.object
  }),
  btn: PropTypes.array
}

export default withState(injectSheet(styles)(OrderPreviewDialog), 'mobile')
