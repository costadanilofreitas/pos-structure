import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { FormattedMessage } from 'react-intl'
import _ from 'lodash'

const DEFAULT_VALUES = {
  '__break__': <br/>
}

const DEFAULT_VALUES_NO_LB = {
  '__break__': ''
}

/**
 * A wrapper around react-intl's `FormattedMessage` that automatically handles messages beginning
 * with `$` and string interpolations separated by the pipe `|` character, which is the standard
 * format used by MW:APP's i18n component.
 *
 * If the message does not starts with `$` it is returned as-is in a wrapper `<span>` element.
 */
class I18N extends PureComponent {
  render() {
    const { noLineBreak } = this.props
    const defaultValues = (noLineBreak) ? DEFAULT_VALUES_NO_LB : DEFAULT_VALUES
    const id = this.props.id || ''

    if (id.startsWith('$')) {
      const props = { ...this.props }
      if (_.includes(id, '|')) {
        const idSplitted = id.split('|')
        props.id = idSplitted[0]
        const values = { ...defaultValues, ...(this.props.values || {}) }
        _.forEach(idSplitted.slice(1), (item, idx) => {
          if (_.includes(item, '\\')) {
            const spanned = _.flatten(
              _.map(
                item.split('\\'),
                (line, idxMsg) => [
                  <span key={`span_${idxMsg}`}>{line}</span>,
                  <br key={`lb_${idxMsg}`}/>
                ]
              )
            )
            values[idx] = <span>{spanned}</span>
          } else {
            values[idx] = item
          }
        })
        props.values = values
      }
      if (!props.values) {
        props.values = defaultValues
      }
      return <FormattedMessage {...props} />
    }
    return <span>{id}</span>
  }
}

I18N.propTypes = {
  id: PropTypes.string,
  values: PropTypes.object,
  noLineBreak: PropTypes.bool
}

I18N.defaultProps = {
  noLineBreak: false
}

export default I18N
