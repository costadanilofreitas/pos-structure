import React from 'react'
import PropTypes from 'prop-types'

const Square2SV = (props) => {
  return (
    <svg height="100%" version="1.1" viewBox="0 0 29 35" width="100%" x="0px" y="0px" {...props}>
      <path fill={props.fill} d="M25.25 32.5L3.27 32.5C1.46 32.5 0 31.04 0 29.23L0 5.74C0 3.93 1.46 2.47 3.27 2.47L25.25 2.47C27.06 2.47 28.52 3.93 28.52 5.74L28.52 29.23C28.52 31.04 27.06 32.5 25.25 32.5Z"/>
      <path fill={props.stroke} d="M19.9 35L8.62 35C8.33 34.96 8.05 34.87 7.79 34.73C7.53 34.59 7.31 34.4 7.12 34.17C6.94 33.94 6.8 33.68 6.71 33.4C6.63 33.12 6.59 32.82 6.62 32.53L22 32.53C22.02 32.83 21.99 33.13 21.9 33.42C21.81 33.71 21.66 33.97 21.46 34.2C21.27 34.43 21.03 34.62 20.76 34.76C20.49 34.89 20.2 34.98 19.9 35L19.9 35Z"/>
      <path fill={props.stroke} d="M8.62 0L19.9 0C20.2 0.02 20.49 0.11 20.76 0.24C21.03 0.38 21.27 0.57 21.46 0.8C21.66 1.03 21.81 1.29 21.9 1.58C21.99 1.87 22.02 2.17 22 2.47L6.57 2.47C6.55 2.17 6.58 1.88 6.67 1.59C6.76 1.31 6.9 1.04 7.09 0.82C7.28 0.59 7.51 0.4 7.77 0.26C8.04 0.12 8.32 0.03 8.62 0L8.62 0Z"/>
    </svg>
  )
}

Square2SV.propTypes = {
  fill: PropTypes.string,
  stroke: PropTypes.string
}

Square2SV.defaultProps = {
  fill: '#f0f1f5',
  stroke: '#898b98'
}

export default Square2SV
