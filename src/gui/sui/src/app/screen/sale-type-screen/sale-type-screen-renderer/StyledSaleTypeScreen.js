import styled from 'styled-components'
import ActionButton from '../../../../component/action-button'

export const MainContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  width: 100%;
  height: 100%;
`

export const BackgroundDiv = styled.div`
  position: fixed;
  width: 100%;
  height: 100%;
`

export const SaleTypeButton = styled(ActionButton)`
  opacity: 0.9;
  height: 25vmin;
  width: 25vmin;
  border-radius: 2vmin;
`

export const SaleTypeText = styled.div`
  display: flex;
  justify-content: space-around;
  color: ${props => props.theme.activeColor};
  font-size: 2.5vmin;
  text-align: center;
`

export const ButtonIcon = styled.i`
  margin: ${props => props.theme.defaultMargin};
  font-size: 5.5vmin;
  text-align: center;
`
