import { PureComponent } from 'react'

const instances = []

export default class AutoFocusComponent extends PureComponent {
  constructor(props) {
    super(props)
    // check if it's already on instances list
    const position = instances.indexOf(this)
    if (position !== -1) {
      instances.splice(position, 1)
    }
    // add this to instances list
    instances.push(this)
  }

  componentWillUnmount = () => {
    // remove this from instances list
    const position = instances.indexOf(this)
    if (position !== -1) {
      instances.splice(position, 1)
    }
  }

  canForceFocus = () => {
    return instances.indexOf(this) === (instances.length - 1)
  }
}
