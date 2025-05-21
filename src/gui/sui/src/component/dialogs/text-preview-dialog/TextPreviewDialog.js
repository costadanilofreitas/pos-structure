import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'
import axios from 'axios'

import { I18N } from '3s-posui/core'
import { ensureArray } from '3s-posui/utils'
import { FlexChild, FlexGrid } from '3s-widgets'

import { IconStyle, PopupStyledButton } from '../../../constants/commonStyles'
import ScrollPanelListItems from '../common/scroll-panel-list-items'
import { isEsc } from '../../../util/keyboardHelper'
import withState from '../../../util/withState'

const styles = (theme) => ({
  messageBackground: {
    position: 'absolute',
    backgroundColor: theme.modalOverlayBackground,
    top: '0',
    left: '0',
    height: '100%',
    width: '100%',
    zIndex: '4',
    alignItems: 'center',
    justifyContent: 'center',
    display: 'flex'
  },
  message: {
    position: 'relative',
    minHeight: 'calc(100% / 12 * 10)',
    background: 'white',
    display: 'flex',
    flexDirection: 'column',
    '@media (max-width: 720px)': {
      width: '100%'
    }
  },
  messageTitle: {
    flex: '1',
    display: 'flex',
    flexDirection: 'column',
    fontSize: '3.0vmin',
    fontWeight: 'bold',
    textAlign: 'center',
    justifyContent: 'center',
    minHeight: '100%',
    color: theme.pressedColor,
    backgroundColor: theme.pressedBackgroundColor
  },
  centerText: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  textPreviewButton: {
    height: '5vh !important',
    backgroundColor: theme.popupsBackgroundColor,
    color: theme.fontColor,
    fontWeight: 'bold',
    '&:active': {
      backgroundColor: theme.pressedBackgroundColor,
      color: theme.pressedColor
    }
  },
  textPreviewButtonSelected: {
    backgroundColor: theme.activeBackgroundColor,
    color: theme.activeColor,
    fontWeight: 'bold'
  },
  lineSeparator: {
    borderRight: '1px solid #cccccc'
  }
})

class TextPreviewDialog extends Component {
  constructor(props) {
    super(props)
    this.onTheFly = this.props.contents.Texts['@attributes'].onTheFly === 'true'
    this.textList = ensureArray(this.props.contents.Texts.PreviewText).map((text) => {
      return {
        key: text['@attributes'].key,
        descr: text['@attributes'].descr,
        content: this.onTheFly ? text['#text'] : text
      }
    })
    this.state = {
      selected: null,
      loadingText: false,
      content: null,
      visible: true
    }

    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleOnPrint = this.handleOnPrint.bind(this)
    this.handleClick = this.handleClick.bind(this)
  }

  render() {
    const { selected, loadingText, content, visible } = this.state
    const { classes, title, mobile } = this.props

    if (!visible) {
      return null
    }

    return (
      <div className={classes.messageBackground}>
        <div className={classes.message} style={{ width: mobile ? '100%' : '70%' }}>
          <div className={'absoluteWrapper'}>
            <FlexGrid direction={'column'}>
              <FlexChild size={1}>
                <div className={classes.messageTitle}>
                  <I18N id={title}/>
                </div>
              </FlexChild>
              <FlexChild size={8}>
                <FlexGrid direction={'row'}>
                  <FlexChild size={1}>
                    <ScrollPanelListItems listItems={this.textList} selected={selected} handleClick={this.handleClick}/>
                  </FlexChild>
                  <FlexChild size={1}>
                    {selected != null && !loadingText &&
                      <div className={classes.centerText}>
                        <pre className={classes.textPreviewContent}>
                          {_.has(content, '#text') ? content['#text'] : (content || '')}
                        </pre>
                      </div>
                    }
                    {selected != null && loadingText &&
                      <div className={classes.textPreviewLoadingCont}>
                        <div className={classes.textPreviewLoadingSpinner} />
                      </div>
                    }
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
              <FlexChild size={1}>
                <FlexGrid>
                  <FlexChild>
                    <PopupStyledButton
                      className={'test_TextPreviewDialog_CLOSE'}
                      onClick={this.handleOnCancel}
                      active={true}
                      borderRight={true}
                    >
                      <IconStyle className="fa fa-ban fa-2x" aria-hidden="true" secondaryColor={true}/><br/>
                      <I18N id="$CLOSE"/>
                    </PopupStyledButton>
                  </FlexChild>
                  <FlexChild>
                    <PopupStyledButton
                      onClick={this.handleOnPrint}
                      active={true}
                    >
                      <IconStyle className="fa fa-file-alt fa-2x" aria-hidden="true" secondaryColor={true}/><br/>
                      <I18N id="$PRINT"/>
                    </PopupStyledButton>
                  </FlexChild>
                </FlexGrid>
              </FlexChild>
            </FlexGrid>
          </div>
        </div>
      </div>
    )
  }

  componentDidMount() {
    document.addEventListener('keydown', this.onKeyPressed.bind(this), false)
  }
  componentWillUnmount() {
    document.removeEventListener('keydown', this.onKeyPressed.bind(this), false)
  }

  onKeyPressed(event) {
    if (isEsc(event)) {
      this.handleOnCancel()
    }
  }

  handleClick(idx, content) {
    if (this.onTheFly) {
      this.setState({
        loadingText: true,
        content: null,
        selected: idx
      })
      axios.get(content).then((response) => {
        this.setState({
          loadingText: false,
          content: response.data
        })
      }, (error) => {
        console.error(error)
        this.setState({
          loadingText: false,
          content: null
        })
      })
    } else {
      this.setState({
        content,
        selected: idx
      })
    }
  }

  handleOnCancel() {
    this.props.closeDialog('1')
  }

  handleOnPrint() {
    if (this.state.selected == null) {
      return
    }
    this.props.closeDialog('0', this.textList[this.state.selected].key)
  }
}


TextPreviewDialog.propTypes = {
  classes: PropTypes.object,
  closeDialog: PropTypes.func,
  title: PropTypes.string,
  message: PropTypes.string,
  mobile: PropTypes.bool,
  default: PropTypes.string,
  contents: {
    Texts: {
      ['@attributes']: {},
      PreviewText: []
    }
  }
}

export default injectSheet(styles)(withState(TextPreviewDialog, 'mobile'))
