import FilterableListBox from './BordereauDialog'
import withStaticConfig from '../../../app/util/withStaticConfig'
import withChangeDialog from '../../../app/util/withChangeDialog'
import withState from '../../../util/withState'

export default withChangeDialog(withStaticConfig(withState(FilterableListBox, 'mobile', 'tefAvailable')))
