import React from 'react'
import { connect } from 'react-redux'


function convertStatetoCamelCase(parts) {
  let propName = ''
  parts.forEach(part => {
    propName += propName === '' ? part : part.charAt(0).toUpperCase() + part.slice(1)
  })
  return propName
}

function withState(ComponentClass, ...states) {
  let mapDispatchToProps = null
  let propsStates = states

  if (states.length > 0 && typeof states[0] === 'function') {
    mapDispatchToProps = states[0]
    propsStates = states.slice(1)
  }

  function mapStateToProps(globalState) {
    const ret = {}
    propsStates.forEach(state => {
      const parts = state.split('.')
      let value = globalState

      const propName = convertStatetoCamelCase(parts)
      parts.some(part => {
        if (value[part] !== null) {
          value = value[part]
          return false
        }
        value = null
        return true
      })

      ret[propName] = value
    })

    return ret
  }

  return connect(mapStateToProps, mapDispatchToProps)(
    function WithState(props) {
      return (<ComponentClass {...props}/>)
    })
}

export default withState
