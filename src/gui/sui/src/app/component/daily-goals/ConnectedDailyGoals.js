import { connect } from 'react-redux'
import DailyGoals from './DailyGoals'
import withState from '../../../util/withState'


function mapStateToProps(state) {
  return {
    dailyGoals: state.custom.DAILY_GOALS == null ? null : JSON.parse(state.custom.DAILY_GOALS)
  }
}

export default connect(mapStateToProps)(withState(DailyGoals, 'theme'))
