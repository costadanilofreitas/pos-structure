import ItemModifier from './ItemModifier'
import withState from '../../../util/withState'
import withStaticConfig from '../../util/withStaticConfig'

export default withState(withStaticConfig(ItemModifier), 'modifiers', 'mobile', 'deviceType')
