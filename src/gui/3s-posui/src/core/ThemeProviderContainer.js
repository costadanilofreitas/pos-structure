import { connect } from 'react-redux'
import { ThemeProvider } from 'react-jss'

const DEFAULT_THEME = {}

function mapStateToProps({ theme }) {
  return {
    theme: theme || DEFAULT_THEME
  }
}

export default connect(mapStateToProps)(ThemeProvider)
