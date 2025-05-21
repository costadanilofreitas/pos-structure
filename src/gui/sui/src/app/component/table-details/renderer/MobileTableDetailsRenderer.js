import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import Label from '../../../../component/label'
import PopMenu from '../../../../component/pop-menu'

export default class MobileTableDetailsRenderer extends Component {
  constructor(props) {
    super(props)

    this.ref = null

    this.state = {
      showingDetails: false
    }

    this.handleOnCollapseClick = this.handleOnCollapseClick.bind(this)
  }

  render() {
    const { tableInfo, classes } = this.props
    const { showingDetails } = this.state

    function renderDetail(detail) {
      return (
        <div key={detail.id} className={classes.tableInfoItems}>
          <p className={`${classes.tableInfoItemsLeft} test_TableDetailsRenderer_INFOLEFT`}>
            <i className={`${detail.icon} fa-x ${classes.tableInfoFaIcon}`} aria-hidden="true"/>
            <I18N id={detail.label}/>
          </p>
          <p className={`${classes.tableInfoRight} test_TableDetailsRenderer_INFORIGHT`}>
            <Label key="totalDivided" text={detail.value} style={detail.labelStyle}/>
          </p>
        </div>
      )
    }

    const icon = showingDetails ? 'fa-angle-down' : 'fa-angle-right'
    return (
      <PopMenu
        containerClassName={'container'}
        menuVisible={showingDetails}
        menuClassName={classes.popUpContainer}
        controllerRef={this.ref}
      >
        <div className={classes.tableInfoBox}>
          <div className={classes.titleContainer} ref={ref => (this.ref = ref)}>
            <span className={classes.detailsTitle}>
              <I18N id={tableInfo.title}/>
            </span>
            <i
              className={`${classes.collapseIcon} fas fa-2x ${icon} test_TableDetailsRenderer_RIGHT`}
              onClick={this.handleOnCollapseClick}
            />
          </div>
        </div>
        <div className={classes.tableInfo}>
          {tableInfo.details.map((detail) => renderDetail(detail))}
        </div>
      </PopMenu>
    )
  }

  handleOnCollapseClick() {
    this.setState({ showingDetails: !this.state.showingDetails })
  }
}

MobileTableDetailsRenderer.propTypes = {
  tableInfo: PropTypes.shape({
    title: PropTypes.string,
    details: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.string,
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      labelStyle: PropTypes.string,
      icon: PropTypes.string
    }))
  }),
  classes: PropTypes.object
}
