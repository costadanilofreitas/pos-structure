import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { FlexChild, FlexGrid } from '3s-widgets'
import StaticConfigPropTypes from '../../../../prop-types/StaticConfigPropTypes'

import { findChildByType } from '../../../../util/renderUtil'
import Banner from '../../../component/banner'
import Footer from '../../../component/footer'

export default class TotemMainScreenRenderer extends Component {
  constructor(props) {
    super(props)
  }

  getScreenOrientation(staticConfig) {
    const isHorizontal = staticConfig.totemConfigurations.banner.horizontal
    const bannerSide = staticConfig.totemConfigurations.banner.side

    if (isHorizontal) {
      if (bannerSide === 'left') {
        return 'row'
      }
      return 'row-reverse'
    }
    return 'column'
  }

  render() {
    const { children, staticConfig, classes } = this.props

    return (
      <FlexGrid direction={'column'} className={classes.rootContainer}>
        <FlexChild size={11.5}>
          <FlexGrid direction={this.getScreenOrientation(staticConfig)}>
            {findChildByType(children, Banner) &&
            <FlexChild size={2} outerClassName={classes.totemBannerContainer}>
              <div className={'absoluteWrapper'}>
                {findChildByType(children, Banner)}
              </div>
            </FlexChild>
            }
            <FlexChild size={9.5} outerClassName={classes.contentContainer}>
              <div className={'absoluteWrapper'}>
                {children[1]}
              </div>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
        <FlexChild size={0.5} outerClassName={classes.totemFooterContainer}>
          <div className={'absoluteWrapper'}>
            {findChildByType(children, Footer)}
          </div>
        </FlexChild>
      </FlexGrid>
    )
  }
}

TotemMainScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  staticConfig: StaticConfigPropTypes,
  classes: PropTypes.object
}
