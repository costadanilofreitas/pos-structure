import React, { Component } from 'react'
import PropTypes from 'prop-types'

class BlockDialogRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const classes = this.props.classes || {}

    return (
      <div className={classes.container}>
        <i className={`fa fa-spinner fa-4x ${classes.loadingIcon}`} aria-hidden="true"/>
      </div>
    )
  }
}

BlockDialogRenderer.propTypes = {
  classes: PropTypes.object
}

export default BlockDialogRenderer
