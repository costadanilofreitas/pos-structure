import React from 'react'
import PropTypes from 'prop-types'


export default function DesktopOrderTotalRenderer({ totalOrder }) {
  const { classes } = this.props
  return (
    <div className={classes.divOrderTotal}>
      <p className={classes.p}>ORDER TOTAL R$: {totalOrder}</p>
    </div>
  )
}

DesktopOrderTotalRenderer.propTypes = {
  totalOrder: PropTypes.number
}
