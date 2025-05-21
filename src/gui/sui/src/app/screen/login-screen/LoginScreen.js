import React from 'react'
import LoginScreenRenderer from './renderer'
import LoginInfo from '../../component/login-info'
import LogoEdeploy from '../../../icon/LogoEdeploy'
import LoginNumpad from '../../component/login-numpad'
import { Desktop, Mobile } from '../../../component/device-selector'
import Dashboard from '../../component/dashboard'

export default function LoginScreen() {
  return (
    <LoginScreenRenderer>
      <LogoEdeploy/>
      <LoginNumpad/>
      <Desktop><Dashboard/></Desktop>
      <Mobile><LoginInfo/></Mobile>
    </LoginScreenRenderer>
  )
}
