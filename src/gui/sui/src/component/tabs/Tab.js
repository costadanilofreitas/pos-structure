import React from 'react'
import PropTypes from 'prop-types'


export default function Tab(props) {
  const { label, isActive, onClick, classes } = props
  let tabClasses = classes.tab
  if (isActive) {
    tabClasses += ` ${classes.activeTab}`
  }
  return (
    <li className={tabClasses} onClick={onClick}>
      <label>{label}</label>
    </li>
  )
}

Tab.propTypes = {
  label: PropTypes.string.isRequired,
  isActive: PropTypes.bool,
  onClick: PropTypes.func,

  classes: PropTypes.object
}
