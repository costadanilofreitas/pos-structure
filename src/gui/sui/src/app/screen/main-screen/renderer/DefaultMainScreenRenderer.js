import React from 'react'
import PropTypes from 'prop-types'

import { findChildByType } from '../../../../util/renderUtil'
import Header from '../../../component/header'
import Footer from '../../../component/footer'
import DeviceType from '../../../../constants/Devices'


function getClassesByDevice(deviceType, classes) {
  let headerClass
  let footerClass
  if (deviceType === DeviceType.Mobile) {
    headerClass = classes.mobileHeaderContainer
    footerClass = classes.mobileFooterContainer
  } else {
    headerClass = classes.headerContainer
    footerClass = classes.footerContainer
  }

  return { headerClass, footerClass }
}

export default function DefaultMainScreenRenderer({ children, deviceType, classes }) {
  const { headerClass, footerClass } = getClassesByDevice(deviceType, classes)

  return (
    <div className={classes.rootContainer}>
      <div className={headerClass}>
        <div className={'absoluteWrapper'}>
          {findChildByType(children, Header)}
        </div>
      </div>
      <div className={classes.contentContainer}>
        <div className={'absoluteWrapper'}>
          {children[1]}
        </div>
      </div>
      <div className={footerClass}>
        <div className={'absoluteWrapper'}>
          {findChildByType(children, Footer)}
        </div>
      </div>
    </div>
  )
}

DefaultMainScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  deviceType: PropTypes.number,
  classes: PropTypes.object
}
