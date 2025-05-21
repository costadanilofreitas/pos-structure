import React from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'

import Label from '../../../../component/label'


export default function DesktopTableDetailsRenderer({ tableInfo, compact, classes }) {
  function renderDetail(detail) {
    if (compact && detail.compact !== true) {
      return null
    }

    return (
      <FlexGrid key={detail.id} direction={'row'}>
        <FlexChild size={compact ? 1 : 3} innerClassName={classes.alignFlexItems}>
          <i
            className={`${detail.icon} fa-x ${classes.tableInfoFaIcon} test_TableDetailsRenderer_TABLEINFO`}
            aria-hidden="true"
          />
          {compact !== true && <I18N id={detail.label}/>}
        </FlexChild>
        <FlexChild size={3} innerClassName={classes.alignFlexItems}>
          <Label
            key={`${detail.id}.label`}
            text={detail.value}
            style={detail.labelStyle}
            className={`${classes.labelInfo}`}
          />
        </FlexChild>
      </FlexGrid>
    )
  }

  return (
    <FlexGrid direction={'column'} className={classes.tableInfoBox}>
      <FlexChild size={1}>
        <div className={classes.titleContainer}>
          <span className={classes.detailsTitle} style={compact ? { fontSize: '1.8vmin' } : {}}>
            <I18N id={tableInfo.title}/>
          </span>
        </div>
      </FlexChild>
      <FlexChild size={4} innerClassName={classes.tableInfo}>
        {tableInfo.details.map((detail) => renderDetail(detail))}
      </FlexChild>
    </FlexGrid>)
}

DesktopTableDetailsRenderer.propTypes = {
  tableInfo: PropTypes.shape({
    title: PropTypes.string,
    number: PropTypes.string,
    details: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.string,
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      labelStyle: PropTypes.string,
      icon: PropTypes.string
    }))
  }),
  compact: PropTypes.bool,
  classes: PropTypes.object
}
