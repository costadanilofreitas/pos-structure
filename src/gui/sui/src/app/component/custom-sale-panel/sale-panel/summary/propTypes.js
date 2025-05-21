import PropTypes from 'prop-types'
import MessageBusPropTypes from '../../../../../prop-types/MessageBusPropTypes'

export default {
  classes: PropTypes.object,
  order: PropTypes.object.isRequired,
  showSummaryOnFinished: PropTypes.bool,
  showSummarySubtotal: PropTypes.bool,
  showSummaryDelivery: PropTypes.bool,
  showSummaryService: PropTypes.bool,
  showSummaryDiscount: PropTypes.bool,
  showSummaryTotalAfterDiscount: PropTypes.bool,
  showSummaryTax: PropTypes.bool,
  showSummaryTotal: PropTypes.bool,
  showSummaryTip: PropTypes.bool,
  showSummaryDue: PropTypes.bool,
  showSummaryChange: PropTypes.bool,
  showSummaryPayment: PropTypes.bool,
  deliveryPLUs: PropTypes.array,
  l10n: PropTypes.object,
  summaryCustomTop: PropTypes.node,
  summaryCustomBottom: PropTypes.node,
  showScrollTenders: PropTypes.bool,
  handleOnTotal: PropTypes.func,
  deleteLines: PropTypes.func,
  msgBus: MessageBusPropTypes,
  saleSummaryStyle: PropTypes.string,
  centralizeSummaryTotal: PropTypes.bool
}

export const defaultProps = {
  order: {},
  l10n: {}
}
