import React from 'react'
import PropTypes from 'prop-types'

const ShiftIcon = ({ viewBox = '0 0 32 32', width = 24, height = 24, fill }) =>
  <svg {...{ width, height, fill, viewBox }}>
    <path d="M21 28h-10c-0.552 0-1-0.448-1-1v-11h-4c-0.404 0-0.769-0.244-0.924-0.617s-0.069-0.804 0.217-1.090l10-10c0.391-0.39 1.024-0.39 1.414 0l10 10c0.286 0.286 0.372 0.716 0.217 1.090s-0.519 0.617-0.924 0.617h-4v11c0 0.552-0.448 1-1 1zM12 26h8v-11c0-0.552 0.448-1 1-1h2.586l-7.586-7.586-7.586 7.586h2.586c0.552 0 1 0.448 1 1v11z" />
  </svg>

ShiftIcon.propTypes = {
  viewBox: PropTypes.string,
  fill: PropTypes.string,
  width: PropTypes.number,
  height: PropTypes.number
}

export default ShiftIcon
