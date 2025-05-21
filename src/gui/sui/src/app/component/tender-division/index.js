import JssTenderDivision from './JssTenderDivision'
import withStaticConfig from '../../util/withStaticConfig'
import withState from '../../../util/withState'

export default withStaticConfig(withState(JssTenderDivision, 'deviceType'))
