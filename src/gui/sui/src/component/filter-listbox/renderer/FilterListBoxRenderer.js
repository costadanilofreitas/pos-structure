import React from 'react'
import { I18N } from '3s-posui/core'
import PropTypes from 'prop-types'

import { FlexGrid, FlexChild, ScrollPanel } from '3s-widgets'

import { findChildByType } from '../../../util/renderUtil'
import { NumPad } from '../../dialogs/numpad-dialog'

export default function FilterListBoxRenderer(props) {
  const { children, classes, title, list, showFilter, direction, scrollY } = props

  const listItemClass = showFilter ? classes.listItem : classes.listItemNoFilter
  const activeItem = `${listItemClass} ${classes.listItemSelected}`
  const showTitle = (title !== '' && title != null)
  const flexDirection = direction === 'column' ? 'column' : 'row'

  function renderItems() {
    return list.map((value, index) => (
      <p
        key={index}
        className={props.chosenValue !== value ? listItemClass : activeItem}
        onClick={() => props.onItemSelect(list.indexOf(value))}
      >
        {value}
      </p>)
    )
  }

  function renderFilter() {
    if (showFilter) {
      const style = direction === 'column' ? { borderTop: '1px solid #ccc' } : { borderLeft: '1px solid #ccc' }

      return (
        <FlexChild>
          <div className={classes.numPadContainer} style={style}>
            <div className={classes.absoluteWrapper}>
              {findChildByType(children, NumPad)}
            </div>
          </div>
        </FlexChild>)
    }
    return null
  }

  function renderTitle() {
    if (showTitle) {
      return (
        <FlexChild size={1} style={{ height: '100%', width: '100%' }}>
          <div className={classes.filterListBoxTitle}>
            <I18N id={title}/>
          </div>
        </FlexChild>
      )
    }
    return null
  }

  return (
    <div className={classes.absoluteWrapper} >
      <FlexGrid direction={'column'}>
        {renderTitle()}
        <FlexChild size={6}>
          <FlexGrid direction={flexDirection}>
            <FlexChild>
              <ScrollPanel styleCont={scrollY === true ? { overflowY: 'auto' } : {}}>
                {renderItems()}
              </ScrollPanel>
            </FlexChild>
            {renderFilter()}
          </FlexGrid>
        </FlexChild>
      </FlexGrid>
    </div>
  )
}

FilterListBoxRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  classes: PropTypes.object,
  title: PropTypes.string,
  list: PropTypes.array,
  chosenValue: PropTypes.string,
  onItemSelect: PropTypes.func,
  showFilter: PropTypes.bool,
  direction: PropTypes.string,
  scrollY: PropTypes.bool
}
