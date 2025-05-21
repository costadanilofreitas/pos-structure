import { connect } from 'react-redux'
import { IntlProvider } from 'react-intl'

function mapStateToProps(state) {
  const locale = state.locale || {}
  return {
    key: locale.language || 'en',
    locale: locale.language || 'en',
    messages: locale.messages,
    formats: locale.formats
  }
}

export default connect(mapStateToProps)(IntlProvider)
