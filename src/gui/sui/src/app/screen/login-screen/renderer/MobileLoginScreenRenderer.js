import React from 'react'
import PropTypes from 'prop-types'
import LogoEdeploy from '../../../../icon/LogoEdeploy'
import LoginInfo from '../../../component/login-info'
import LoginNumpad from '../../../component/login-numpad'
import { findChildByType } from '../../../../util/renderUtil'

export default function MobileLoginScreenRenderer({ children, classes }) {
  return (
    <div className={classes.mobileRootContainer}>
      <div className={classes.infoContainer}>
        <div className={classes.mobileLogoContainer}>
          <div className={'absoluteWrapper'}>
            {findChildByType(children, LogoEdeploy)}
          </div>
        </div>
        <div className={classes.loginInfoContainer}>
          <div className={'absoluteWrapper'}>
            {findChildByType(children, LoginInfo)}
          </div>
        </div>
      </div>
      <div className={classes.numpadContainer}>
        <div className={'absoluteWrapper'}>
          {findChildByType(children, LoginNumpad)}
        </div>
      </div>
    </div>
  )
}

MobileLoginScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  classes: PropTypes.object
}
