import React from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { ensureDecimals } from '3s-posui/utils'

import { FormattedDate, FormattedNumber } from 'react-intl'


function getTimeFromMilliSeconds(milliseconds) {
  let seconds = Math.floor((milliseconds / 1000) % 60)
  let minutes = Math.floor((milliseconds / (1000 * 60)) % 60)
  let hours = (Math.floor(milliseconds / (1000 * 3600) / 24) * 24) + Math.floor((milliseconds / (1000 * 3600)) % 24)

  hours = (hours < 10) ? `0${hours}` : hours
  minutes = (minutes < 10) ? `0${minutes}` : minutes
  seconds = (seconds < 10) ? `0${seconds}` : seconds

  return `${hours}:${minutes}:${seconds}`
}

export default function Label(props) {
  function utcTimeNow() {
    return new Date(props.getCurrentDate().getTime() + (props.getCurrentDate().getTimezoneOffset() * 60000))
  }

  switch (props.style) {
    case 'currency':
      return (
        <FormattedNumber
          style="currency"
          value={props.text}
          currency={props.currency ? props.currency : 'BRL'}
          minimumFractionDigits={props.decimalPlaces || 2}
          maximumFractionDigits={props.decimalPlaces || 2}
        />
      )
    case 'datetime':
      return (
        <FormattedDate
          value={props.text}
          year={'numeric'}
          month={'numeric'}
          day={'numeric'}
          hour={'numeric'}
          minute={'numeric'}
          second={'numeric'}
        />
      )
    case 'decimal':
      return <span>{ensureDecimals(props.text, props.decimalPlaces, props.decimalSeparator)}</span>
    case 'date':
      return (
        <FormattedDate
          value={props.text}
          year={'numeric'}
          month={'numeric'}
          day={'numeric'}
        />
      )
    case 'hourMinuteSecond':
      return (
        <FormattedDate
          value={props.text}
          hour={'numeric'}
          minute={'numeric'}
          second={'numeric'}
        />
      )
    case 'hourMinute':
      return (
        <FormattedDate
          value={props.text}
          hour={'numeric'}
          minute={'numeric'}
        />
      )
    case 'hourMinuteSecondDiffForNow':
      return <span>{getTimeFromMilliSeconds(props.getCurrentDate() - props.text)}</span>
    case 'hourMinuteSecondDiffForNowUTC':
      return <span>{getTimeFromMilliSeconds(utcTimeNow() - props.text)}</span>
    case 'datetimeMillisecondsSpan':
      return <span>{getTimeFromMilliSeconds(props.text)}</span>
    default:
      if (props.text && props.text.indexOf && props.text.indexOf('$') === 0) {
        return <span onClick={props.onClick} className={props.className}><I18N id={props.text}/></span>
      }
  }

  return (
    <span
      onClick={props.onClick}
      className={props.className}
    >
      {props.text}
    </span>
  )
}

Label.propTypes = {
  getCurrentDate: PropTypes.func,
  text: PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.object]),
  style: PropTypes.string,
  currency: PropTypes.string,
  className: PropTypes.string,
  onClick: PropTypes.func,
  decimalPlaces: PropTypes.string,
  decimalSeparator: PropTypes.string
}
