import PrepLines from './PrepLines'
import withState from '../../../../util/withState'

export default withState(
  PrepLines,
  'currentLine',
  'zoom',
  'timeDelta',
  'kdsModel')
