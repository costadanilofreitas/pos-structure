import PropTypes from 'prop-types'

const StaticConfigPropTypes = PropTypes.shape({
  spinnerConfig: PropTypes.shape({
    type: PropTypes.string,
    enabled: PropTypes.bool
  }),
  timeToAlertTableIsIdleWarning: PropTypes.number,
  recallButton: PropTypes.bool,
  operatorButton: PropTypes.bool,
  cashPaymentEnabled: PropTypes.bool,
  discountsEnabled: PropTypes.bool,
  billPaymentEnabled: PropTypes.bool,
  tenderTypes: PropTypes.arrayOf(PropTypes.shape(
    {
      id: PropTypes.number,
      parentId: PropTypes.number,
      showInFC: PropTypes.bool,
      showInDL: PropTypes.bool
    }
  )),
  specialMenus: PropTypes.arrayOf(PropTypes.string),
  navigationOptions: PropTypes.shape({
    showBarcodeScreen: PropTypes.bool,
    showSearchScreen: PropTypes.bool
  }),
  timeToAlertTableOpened: PropTypes.number,
  fetchStoredOrdersTimeout: PropTypes.number,
  enablePreStartSale: PropTypes.bool,
  priceOverrideEnabled: PropTypes.bool,
  enabledTags: PropTypes.arrayOf(PropTypes.string),
  canOpenTableFromAnotherOperator: PropTypes.bool,
  showInDashboard: PropTypes.array,
  cancelTimeoutWindow: PropTypes.number,
  canEditOrder: PropTypes.bool,
  productsScreenDimensions: PropTypes.object,
  availableSaleTypes: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)),
  showCashInAndCashOut: PropTypes.bool,
  screenTimeout: PropTypes.number,
  satInfo: PropTypes.shape({
    enabled: PropTypes.bool,
    working: PropTypes.bool
  }),
  remoteOrderStatus: PropTypes.shape({
    enabled: PropTypes.bool,
    isOnline: PropTypes.bool,
    isOpened: PropTypes.bool,
    lastExternalContact: PropTypes.string,
    closedSince: PropTypes.string,
    working: PropTypes.bool,
    fetchTimeout: PropTypes.number
  }),
  enableTabBtns: PropTypes.bool,
  timeToAlertTableIsIdle: PropTypes.number,
  timeToAlertRecallDeliveryIsIdle: PropTypes.number,
  productionCourses: PropTypes.object,
  totemConfigurations: PropTypes.shape({
    navigation: PropTypes.shape({
      horizontal: PropTypes.bool,
      showSearchScreen: PropTypes.bool,
      showBarcodeScreen: PropTypes.bool
    }),
    cart: PropTypes.shape({
      horizontal: PropTypes.bool
    }),
    welcomeScreen: PropTypes.shape({
      backgroundFormat: PropTypes.string,
      showPopup: PropTypes.bool
    }),
    saleType: PropTypes.shape({
      showImage: PropTypes.bool
    }),
    banner: PropTypes.shape({
      horizontal: PropTypes.bool,
      side: PropTypes.string
    }),
    confirmationScreen: PropTypes.shape({
      timeout: PropTypes.number
    })
  }),
  posNavigation: PropTypes.string,
  deliverySound: PropTypes.bool,
  deliveryAddress: PropTypes.bool,
  commentButton: PropTypes.bool,
  specialInstructionsEnabled: PropTypes.bool
})

export default StaticConfigPropTypes
