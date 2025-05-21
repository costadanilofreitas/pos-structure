import React from 'react'
import PropTypes from 'prop-types'

const Square4S = (props) => {
  return (
    <svg height="100%" version="1.1" viewBox="0 0 287.3 287.8" width="100%" x="0px" y="0px" {...props}>
      <path d="M196.4,14.6H90.8v0c0 -7.8,6.3 -14.1,14.1 -14.1h77.4C190.1,0.6,196.4,6.9,196.4,14.6L196.4,14.6z" fill={props.stroke} />
      <path d="M90.8,273.7h105.6v0c0,7.8 -6.3,14.1 -14.1,14.1h -77.4C97.1,287.8,90.8,281.5,90.8,273.7L90.8,273.7z" fill={props.stroke} />
      <path d="M273.2,197V91.4h0c7.8,0,14.1,6.3,14.1,14.1v77.4C287.3,190.7,281,197,273.2,197L273.2,197z" fill={props.stroke} />
      <path d="M14.1,91.4V197h0C6.3,197,0,190.7,0,182.9v -77.4C0,97.7,6.3,91.4,14.1,91.4L14.1,91.4z" fill={props.stroke} />
      <path d="M267.5,273.7H19.8c -3.1,0 -5.7 -2.5 -5.7 -5.7V20.3c0 -3.1,2.5 -5.7,5.7 -5.7h247.7c3.1,0,5.7,2.5,5.7,5.7V268  C273.2,271.2,270.6,273.7,267.5,273.7z" fill={props.fill} />
    </svg>
  )
}

Square4S.propTypes = {
  fill: PropTypes.string,
  stroke: PropTypes.string
}

Square4S.defaultProps = {
  fill: '#f0f1f5',
  stroke: '#898b98'
}

export default Square4S
