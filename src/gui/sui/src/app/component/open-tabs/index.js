import OpenTabs from './OpenTabs'
import withState from '../../../util/withState'
import withStaticConfig from '../../util/withStaticConfig'

export default withStaticConfig(withState(OpenTabs, 'workingMode'))
