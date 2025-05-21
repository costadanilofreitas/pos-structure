import PropTypes from 'prop-types'
import OrderPropTypes from './OrderPropTypes'

const TablePropTypes = PropTypes.shape({
  id: PropTypes.string.isRequired,
  type: PropTypes.number,
  typeDescr: PropTypes.string,
  seats: PropTypes.number,
  status: PropTypes.number.isRequired,
  statusDescr: PropTypes.string,
  serviceId: PropTypes.number,
  userId: PropTypes.string,
  serviceSeats: PropTypes.number,
  sector: PropTypes.string,
  startTS: PropTypes.object,
  finishTS: PropTypes.object,
  tabNumber: PropTypes.string,
  linkedTables: PropTypes.arrayOf(PropTypes.string),
  orders: PropTypes.arrayOf(OrderPropTypes).isRequired,
  specialCatalog: PropTypes.string,
  selectedSaleType: PropTypes.string
})

export default TablePropTypes
