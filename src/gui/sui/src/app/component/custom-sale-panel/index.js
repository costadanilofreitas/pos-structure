import JssSalePanel from './JssSalePanelComponent'
import withStaticConfig from '../../util/withStaticConfig'
import withState from '../../../util/withState'
import withGetMessage from '../../../util/withGetMessage'
import withMessageBus from '../../../util/withMessageBus'


export default withMessageBus(withGetMessage(withStaticConfig(
  withState(JssSalePanel, 'builds', 'order', 'products')
)))
