import React, { Component } from 'react'
import PropTypes from 'prop-types'

import JssTableSeatsList from './JssTableSeatsList'
import withShowDialog from '../../../util/withShowDialog'
import withGetMessage from '../../../util/withGetMessage'
import withMirror from '../../util/withMirror'
import withExecuteActionMessageBus from '../../../util/withExecuteActionMessageBus'


function withOnLineChange(ComponentClass) {
  class WithOnLineChange extends Component {
    constructor(props) {
      super(props)
      this.msgBus = props.msgBus
    }

    render() {
      return (
        <ComponentClass
          onLineChange={(saleLines, seat) => {
            this.msgBus.syncAction('change_line_seat', JSON.stringify(saleLines), seat)
          }}
          {...this.props}
        />
      )
    }
  }

  WithOnLineChange.propTypes = {
    msgBus: PropTypes.shape({
      syncAction: PropTypes.func.isRequired
    }).isRequired
  }

  return withExecuteActionMessageBus(WithOnLineChange)
}

export default withMirror(withGetMessage(withShowDialog(withOnLineChange(JssTableSeatsList))))
