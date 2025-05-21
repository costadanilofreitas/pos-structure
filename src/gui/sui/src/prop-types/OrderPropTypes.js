import PropTypes from 'prop-types'

const OrderPropTypes = PropTypes.shape({
  '@attributes': PropTypes.shape({
    state: PropTypes.string,
    dueAmount: PropTypes.string,
    totalGross: PropTypes.string
  }),
  SaleLine: PropTypes.oneOfType([PropTypes.oneOfType([PropTypes.array, PropTypes.object]), PropTypes.object]),
  TenderHistory: PropTypes.shape({
    Tender: PropTypes.arrayOf(PropTypes.shape({
      '@attributes': PropTypes.shape({
        tenderId: PropTypes.string,
        tenderType: PropTypes.string,
        tenderDescr: PropTypes.string,
        timestamp: PropTypes.string,
        timestampGMT: PropTypes.string,
        tenderAmount: PropTypes.string,
        eletronicType: PropTypes.string,
        commentId: PropTypes.string
      })
    }))
  }),
  CustomOrderProperties: PropTypes.shape({
    CUSTOMER_NAME: PropTypes.string,
    CUSTOMER_DOC: PropTypes.string,
    CUSTOMER_PHONE: PropTypes.string,
    POSTAL_CODE: PropTypes.string,
    CITY: PropTypes.string,
    STREET_NAME: PropTypes.string,
    NEIGHBORHOOD: PropTypes.string,
    STREET_NUMBER: PropTypes.string,
    COMPLEMENT: PropTypes.string,
    ADDRESS_REFERENCE: PropTypes.string
  })
})

export default OrderPropTypes
