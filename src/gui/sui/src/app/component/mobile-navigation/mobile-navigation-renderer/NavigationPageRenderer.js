import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'
import isEmpty from 'lodash/isEmpty'
import _map from 'lodash/map'
import { Grid, Row, Col } from '../../../../component/grid'
import NavigationItemRenderer from './NavigationItemRenderer'
import ActionButton from '../../../../component/action-button/JssActionButton'
import Label from '../../../../component/label/Label'


export default class NavigationPageRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { items, groups, showBack, classes } = this.props
    if (isEmpty(groups) && isEmpty((items))) {
      return (
        <Label className={classes.noNavigation} text="$NO_NAVIGATION_AVAILABLE"/>
      )
    }
    return (
      <Grid className={classes.gridCategory}>
        {this.renderItems(groups, true)}
        {this.renderItems(items, false)}
        {showBack && this.renderBackButton()}
      </Grid>
    )
  }

  renderItems(items, isNavigation) {
    const { classes, onClick, products } = this.props
    return _map(items, (row, idx) => (
      <Row key={idx} rowSpace={'calc(100vh / (24 * 6))'} className={classes.paddingButtonCategory}>
        {row.map(item =>
          <Col xs={6} key={idx}>
            <NavigationItemRenderer
              item={item} onClick={onClick} classes={classes} products={products} isNavigation={isNavigation}
            />
          </Col>
        )}
      </Row>
    ))
  }

  renderBackButton() {
    return (
      <Row rowSpace={'0'} className={this.props.classes.backButtonRow}>
        <Col xs={12}>
          <ActionButton
            className={'test_NavigationPageRenderer_BACK'}
            onClick={this.props.onBackClick}
            inlineText={true}
          >
            <i className={'fas fa-arrow-circle-left fa-2x'} aria-hidden="true" style={{ margin: '0.5vh' }}/>
            <I18N id={'$BACK'}/>
          </ActionButton>
        </Col>
      </Row>
    )
  }
}

NavigationPageRenderer.propTypes = {
  classes: PropTypes.object,
  items: PropTypes.array,
  groups: PropTypes.array,
  onClick: PropTypes.func,
  showBack: PropTypes.bool,
  onBackClick: PropTypes.func,
  products: PropTypes.object
}
