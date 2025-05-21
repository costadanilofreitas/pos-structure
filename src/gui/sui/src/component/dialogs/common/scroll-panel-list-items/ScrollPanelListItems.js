import React, { Component } from 'react'
import injectSheet from 'react-jss'
import PropTypes from 'prop-types'

import { ScrollPanel } from '3s-widgets'
import Button from '../../../action-button/Button'


const styles = (theme) => ({
  textPreviewButton: {
    height: '5vh !important',
    backgroundColor: `${theme.backgroundColor} !important`,
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
    height: '100%',
    borderRight: '1px solid #cccccc',
    width: 'calc(100% - 1px)',
    position: 'relative'
  }
})

class ScrollPanelListItems extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, listItems, selected, handleClick } = this.props

    return (
      <div className={classes.lineSeparator}>
        <ScrollPanel className={'ScrollPanelListItems_DOWN'}>
          {listItems.map((text, idx) => {
            const sel = selected === idx
            const textPreviewButtonSelected = (sel) ? classes.textPreviewButtonSelected : ''
            return (
              <Button
                onClick={() => handleClick(idx, text.content)}
                className={`${classes.textPreviewButton} ${textPreviewButtonSelected} test_ScrollPanelListItems_DATE`}
                key={`${text.key}_${idx}_${sel}`}
              >
                {text.descr}
              </Button>
            )
          })}
        </ScrollPanel>
      </div>
    )
  }
}

ScrollPanelListItems.propTypes = {
  classes: PropTypes.object,
  listItems: PropTypes.array,
  selected: PropTypes.number,
  handleClick: PropTypes.func
}

export default injectSheet(styles)(ScrollPanelListItems)
