import React from 'react'
import PropTypes from 'prop-types'
import { findChildByType } from '../../../../util/renderUtil'
import LogoEdeploy from '../../../../icon/LogoEdeploy'
import LoginNumpad from '../../../component/login-numpad'
import Dashboard from '../../../component/dashboard'

export default function DesktopLoginScreenRenderer({ children, classes }) {
  return (
    <div className={classes.desktopRootContainer}>
      <div className={classes.loginContainer}>
        <div className={'absoluteWrapper'}>
          <div className={`${classes.loginInnerContainer} absoluteWrapper test_LoginScreen_CONTAINER`}>
            <div className={classes.desktopLogoContainer}>
              <div className={'absoluteWrapper'}>
                {findChildByType(children, LogoEdeploy)}
              </div>
            </div>
            <div className={classes.numpadContainer}>
              <div className={'absoluteWrapper'}>
                {findChildByType(children, LoginNumpad)}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className={classes.dashboardContainer}>
        <div className={'absoluteWrapper'}>
          {findChildByType(children, Dashboard)}
        </div>
      </div>
    </div>
  )
}

DesktopLoginScreenRenderer.propTypes = {
  children: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  classes: PropTypes.object
}
