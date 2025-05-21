import styled from 'styled-components'
import { FlexChild } from '3s-widgets'

export const Container = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  flex: ${props => props.flex ? props.flex : 1};
`

export const BackgroundDiv = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: ${props => props.withImage ? '1' : '-1'};
`

export const MainOrderContainer = styled(FlexChild)`
  flex-direction: row;
  background-color: ${props => props.theme.pickupBackgroundColor};
`

export const ReadyAndCalledOrdersContainer = styled.div`
  display: flex;
  flex-direction: row;
  position: absolute;
  width: 100%;
  height: 100%;
`
