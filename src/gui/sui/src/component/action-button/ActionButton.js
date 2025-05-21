import React from 'react'
import PropTypes from 'prop-types'

import Button from './Button'


export default function ActionButton(props) {
  const { classes, inlineText } = props

  const disabledClass = inlineText !== true ? classes.disabledButton : `${classes.disabledButton} ${classes.inlineText}`
  const pressedClass = inlineText !== true ? classes.pressedButton : `${classes.pressedButton} ${classes.inlineText}`
  const activeClass = inlineText !== true ? classes.activeButton : `${classes.activeButton} ${classes.inlineText}`

  return (
    <Button
      {...props}
      key={`${props.key}`}
      className={props.selected ? `${pressedClass} ${props.className}` : `${activeClass} ${props.className}`}
      classNamePressed={`${pressedClass} ${props.className}`}
      classNameDisabled={`${disabledClass} ${props.className}`}
      blockOnActionRunning={true}
    />
  )
}

ActionButton.propTypes = {
  classes: PropTypes.object,
  disabled: PropTypes.bool,
  selected: PropTypes.bool,
  inlineText: PropTypes.bool,
  key: PropTypes.string,
  className: PropTypes.string
}
