import React from 'react'
import PropTypes from 'prop-types'

const Square2SH = (props) => {
  return (
    <svg height="100%" version="1.1" viewBox="0 0 35 29" width="100%" x="0px" y="0px" {...props}>
      <path fill={props.fill} d="M2.47 25.25L2.47 3.27C2.47 1.46 3.93 0 5.74 0L29.23 0C31.04 0 32.5 1.46 32.5 3.27L32.5 25.25C32.5 27.06 31.04 28.52 29.23 28.52L5.74 28.52C3.93 28.52 2.47 27.06 2.47 25.25Z" />
      <path fill={props.stroke} d="M0 19.9L0 8.62C0.04 8.33 0.13 8.05 0.27 7.79C0.41 7.53 0.6 7.31 0.83 7.12C1.06 6.94 1.32 6.8 1.6 6.71C1.88 6.63 2.18 6.59 2.47 6.62L2.47 6.62L2.47 22L2.47 22C2.17 22.02 1.87 21.99 1.58 21.9C1.29 21.81 1.03 21.66 0.8 21.46C0.57 21.27 0.38 21.03 0.24 20.76C0.11 20.49 0.02 20.2 0 19.9L0 19.9Z" />
      <path fill={props.stroke} d="M35 8.62L35 19.9C34.98 20.2 34.89 20.5 34.75 20.77C34.61 21.04 34.42 21.28 34.19 21.47C33.96 21.67 33.69 21.82 33.4 21.91C33.11 22 32.8 22.03 32.5 22L32.5 22L32.5 6.57L32.5 6.57C32.8 6.54 33.1 6.57 33.39 6.66C33.67 6.75 33.94 6.89 34.17 7.08C34.41 7.27 34.6 7.5 34.74 7.77C34.88 8.03 34.97 8.32 35 8.62Z" />
    </svg>
  )
}

Square2SH.propTypes = {
  fill: PropTypes.string,
  stroke: PropTypes.string
}

Square2SH.defaultProps = {
  fill: '#f0f1f5',
  stroke: '#898b98'
}

export default Square2SH
