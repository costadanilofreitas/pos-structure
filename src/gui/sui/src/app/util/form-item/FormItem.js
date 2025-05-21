import React from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'


export default function FormItem({ label, value, position, textAlign, classes }) {
  let positionLabel = classes.endLabel
  let positionInput = classes.endInput

  if (position === 'below') {
    positionLabel += ` ${classes.belowLabel}`
    positionInput = classes.belowInput
  }

  let textAlignInput = ''
  if (textAlign === 'center') {
    textAlignInput = classes.textAlignCenter
  } else if (textAlign === 'right') {
    textAlignInput = classes.textAlignRight
  }

  function getValue() {
    if (typeof value === 'string') {
      return <I18N id={value}/>
    }

    return value
  }

  return (
    <div>
      <span className={`${positionLabel} ${classes.label}`}>
        <I18N id={label}/>
        {position !== 'below' ? ':' : ''}
      </span>
      <span className={`${positionInput} ${textAlignInput} ${classes.input}`}>
        <div style={{ marginLeft: '1vmin' }}>
          {getValue()}
        </div>
      </span>
    </div>)
}

FormItem.propTypes = {
  classes: PropTypes.object,
  label: PropTypes.string,
  position: PropTypes.string,
  textAlign: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.object])
}
