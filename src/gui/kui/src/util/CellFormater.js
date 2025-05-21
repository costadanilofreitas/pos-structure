import React from 'react'
import { I18N } from '3s-posui/core'
import { KDSCellTimer } from '3s-posui/widgets'

function splitIncludingDelimiter(value) {
  return value.split(/([\s])/g)
}

function translateMarkedTags(value) {
  return splitIncludingDelimiter(value)
    .map((v, innerIndex) => v.startsWith('$') ? <I18N key={innerIndex} id={v}/> : <span key={innerIndex}>{v}</span>)
}

function parseTags(match, order, tagIndex, timerColor, theme) {
  const macro = match.substring(match.indexOf('{') + 1, match.indexOf('}'))

  if (!match.startsWith('$') && !match.startsWith('#')) {
    if ((match.startsWith('[') || match.startsWith(']')) && timerColor !== null) {
      return <span key={tagIndex} style={{ color: timerColor }}>{match}</span>
    }
    return match
  }

  if (match.startsWith('$')) {
    return (
      <React.Fragment key={tagIndex}>
        {translateMarkedTags(match)}
      </React.Fragment>
    )
  }

  let value = null
  const macroList = macro.split('|')
  for (let i = 0; i < macroList.length; i++) {
    let currentMacro = macroList[i]

    let mod = null
    let pad = false
    const index = currentMacro.indexOf('%')
    if (index !== -1) {
      mod = currentMacro.substring(index + 1)
      if (mod[0] === '0') {
        pad = true
      }
      mod = Number(mod) || null
      currentMacro = currentMacro.substring(0, index)
    }


    switch (currentMacro.toLowerCase()) {
      case 'id': {
        value = order.attrs.order_id
        break
      }
      case 'major': {
        value = order.attrs.major
        break
      }
      case 'minor': {
        value = order.attrs.minor
        break
      }
      case 'pod': {
        value = ''
        // TODO: Remove HARDCODED
        if (order.attrs.pod_type === 'TT' && !order.props.TOTEM_SERVICE) {
          value = `$${order.attrs.pod_type} `
        }
        break
      }
      case 'total': {
        value = L10N.numberToCurrency(Number(this.totalAmount), true)
        break
      }
      case 'tax': {
        value = L10N.numberToCurrency(Number(this.taxAmount), true)
        break
      }
      case 'posid': {
        value = order.attrs.pos_id
        break
      }
      case 'time': {
        const displayTime = order.attrs.display_time_gmt
        if (displayTime != null && displayTime !== '') {
          value = <KDSCellTimer key={tagIndex} startTime={displayTime} style={{ color: timerColor }}/>
        }
        break
      }
      case 'status': {
        value = `$STATUS_${order.attrs.state}`
        break
      }
      case 'eatin': {
        value = ''
        if (order.attrs.sale_type.toUpperCase() === 'EAT_IN') {
          value = `$${order.attrs.sale_type}`
        }
        break
      }
      case 'takeout': {
        value = ''
        if (order.attrs.sale_type.toUpperCase() === 'TAKE_OUT') {
          value = (
            <span key={tagIndex} style={{ color: theme.takeOutColorFont }}>
              <I18N id={`$${order.attrs.sale_type}`}/>
            </span>
          )
        }
        break
      }
      case 'delivery': {
        value = ''
        if (order.attrs.sale_type.toUpperCase() === 'DELIVERY') {
          if (order.props.PARTNER) {
            let textValue = `${order.props.PARTNER}`
            if (order.props.BRAND) {
              textValue += ` - ${order.props.BRAND}`
            }
            value = <span key={tagIndex} style={{ color: theme.deliveryColorFont }}>{textValue}</span>
          } else {
            const fontColor = theme ? theme.deliveryColorFont : '#000'
            value = (
              <span key={tagIndex} style={{ color: fontColor }}>
                <I18N id={`$${order.attrs.sale_type}`}/>
              </span>
            )
          }
        }
        break
      }
      case 'saletype': {
        value = `$${order.attrs.sale_type}`
        break
      }
      case 'operator': {
        value = order.attrs.operator_name
        break
      }
      case 'shortreference': {
        value = order.props.SHORT_REFERENCE
        value = value != null ? `#${value}` : ''
        break
      }
      case 'table': {
        let i18nvalue = ''
        value = order.props.TAB_ID
        if (value != null) {
          i18nvalue = '$TAB'
        } else {
          value = order.props.TABLE_ID
          i18nvalue = '$TABLE'
        }

        if (value) {
          const saleType = (order.attrs.sale_type || '').toUpperCase()

          value = (
            <span key={index}>
              <I18N id={i18nvalue}/>
              &nbsp;
              <I18N id={value}/>
              {saleType === 'TAKE_OUT' &&
              <>
                &nbsp;(
                <I18N id={`$${saleType}`}/>
                )
              </>
              }
            </span>
          )
        }
        break
      }
      case 'recall': {
        value = ''
        if (order.attrs.recalled === 'True') {
          value = <span key={index}>[R]</span>
        }
        break
      }
      case '':
        value = ' '
        break
      default: {
        if (value == null && currentMacro.toLowerCase().indexOf('property:') === 0) {
          const key = currentMacro.substring('property:'.length, currentMacro.length)
          if (key) {
            const propertyKey = key.startsWith('$') ? key.substring(1) : key
            value = order.props[propertyKey]

            if (value != null && key.startsWith('$')) {
              const i18nKey = `$KDS_PROPERTY_${value}`
              value = <I18N key={tagIndex} id={i18nKey}/>
            }
          }
        } else if (value == null && currentMacro.toLowerCase().indexOf('propertykey:') === 0) {
          const key = currentMacro.substring('propertyKey:'.length, currentMacro.length)
          const propertyKey = key.startsWith('$') ? key.substring(1) : key
          value = order.props[propertyKey]

          if (value != null) {
            if (key && key.startsWith('$')) {
              const i18nKey = `$KDS_PROPERTY_${propertyKey}`
              value = <span key={tagIndex}><I18N id={i18nKey}/></span>
            } else {
              value = key
            }
          }
        }

        break
      }
    }

    if (value != null && value !== '') {
      if (mod) {
        value = String(parseInt(value, 10) % mod)
        if (pad) {
          value = value.padStart(String(mod).length - 1, '0')
        }
      }
      break
    }
  }

  if (match === ' ' || value == null) {
    return (
      <React.Fragment key={tagIndex}>&nbsp;</React.Fragment>
    )
  }
  if (React.isValidElement(value)) {
    return value
  }

  return (
    <React.Fragment key={tagIndex}>
      {translateMarkedTags(value != null ? value : match)}
    </React.Fragment>
  )
}

function splitCustomTagsFromTemplate(template) {
  return template.split(/(#{.*?})|(\$[a-zA-Z0-9]*)|([^#$]*)/gi).filter(i => !['', undefined].includes(i))
}

export default function parseMacros(template, order, timerColor = null, theme = null) {
  if (order == null) {
    return ''
  }

  return splitCustomTagsFromTemplate(template).map((tag, index) => parseTags(tag, order, index, timerColor, theme))
}
