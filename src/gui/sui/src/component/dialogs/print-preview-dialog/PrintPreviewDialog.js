import React, { Component } from 'react'
import PropTypes from 'prop-types'
import injectSheet from 'react-jss'

import MessageOptionsDialog from '../message-options-dialog'

const styles = (theme) => ({
  printPreview: {
    whiteSpace: 'pre',
    fontFamily: 'monospace',
    textAlign: 'left',
    fontSize: '1.3em',
    margin: '0.3em'
  }
})

class PrintPreviewDialog extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, contents, mobile } = this.props

    if (contents == null) {
      return null
    }

    let text
    const contentText = contents['#text'].split('\n')
    if (contentText.length === 1 && contentText[0].startsWith('<span')) {
      text = [<div key="only" dangerouslySetInnerHTML={{ __html: contents['#text'] }} />]
    } else {
      text = []
      for (let i = 0; i < contentText.length; i++) {
        text.push(<p key={`printPreview_${i}`} className={classes.printPreview}>{contentText[i]}</p>)
      }
    }

    return <MessageOptionsDialog {...this.props} message={text} isPrintPreview={true} scrollY={mobile === true}/>
  }
}

PrintPreviewDialog.propTypes = {
  classes: PropTypes.object,
  contents: PropTypes.object,
  mobile: PropTypes.bool
}

export default injectSheet(styles)(PrintPreviewDialog)
