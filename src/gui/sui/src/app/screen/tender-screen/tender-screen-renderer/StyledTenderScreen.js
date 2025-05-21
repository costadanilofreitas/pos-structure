import styled from 'styled-components'

import { FlexChild } from '3s-widgets'
import ActionButton from '../../../../component/action-button'

export const SalePanelContainer = styled.div`
  margin: 0 ${props => props.theme.defaultPadding} 0 ${props => props.theme.defaultPadding};
  background: ${props => props.theme.backgroundColor};
  height: 100%;
`
export const MainContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  width: 100%;
  height: 100%;
`

export const MainTitle = styled.div`
  display: flex;
  height: 30%;
  justify-content: center;
  align-items: center;
  font-size: 2.5vmin;
  font-weight: bold;
`

export const FlexChildAligner = styled(FlexChild)`
  display: flex;
  height: 100%;
  width: 100%;
  justify-content: center;
  align-items: center;
`

export const CustomerButton = styled(ActionButton)`
  opacity: 0.9;
  height: 90%;
  width: 90%;
  border-radius: 1vmin;
`

export const CustomerInfoContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #000;
  height: 100% ;
  width: 100%;
`

export const CustomerInfoTable = styled.div`
  display: flex;
  text-align: center;
  justify-content: center;
  height: 100%;
  width: 50%;
`

export const CustomerName = styled.div`
  width: 100%;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
`

export const ReturnContainer = styled.div`
  display: flex;
  height: 100%;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: #FFFFFF;
  opacity: 0.5;
`

export const ReturnDiv = styled.div`
  display: flex;
  justify-content: center;
  width: 10%;
  align-items: center;
`
export const ReturnText = styled.div`
  font-weight: bold;
  font-size: 2.5vmin;
  color: ${props => props.theme.activeBackgroundColor};
`
export const BackgroundDiv = styled.div`
  position: fixed;
  width: 100%;
  height: 100%;
`
export const AddressTitle = styled.div`
  font-size: 1.5vmin;
  line-height: 1.5vmin;
  margin: 1vmin;
  color: ${props => props.theme.commonStyledButtonColor};
  font-weight: bold;
  text-transform: uppercase;
`
export const AddressContent = styled.p`
  font-size: 1.5vmin;
  margin: 1vmin;
  color: ${props => props.theme.commonStyledButtonColor};
  overflow: hidden;
  line-height: 1.5vmin;
  white-space: nowrap;
  text-overflow: ellipsis;
  text-transform: uppercase;
`

