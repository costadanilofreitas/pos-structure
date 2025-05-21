import styled from 'styled-components'
import ActionButton from '../../../../component/action-button'

export const MainContainer = styled.div`
  background-color: #fff;
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
  opacity: 0.2;
`

export const SummaryButton = styled(ActionButton)`
  opacity: 0.9;
  height: 13vmin;
  width: 15vmin;
  border-radius: 2vmin;
`

export const SummaryButtonText = styled.div`
  display: flex;
  justify-content: space-around;
  font-size: 2.5vmin;
  text-align: center;
  color: ${props => props.theme.activeColor};
`

export const ButtonIcon = styled.i`
  margin: ${props => props.theme.defaultMargin};
  font-size: 5.5vmin;
  text-align: center;
`
export const SummaryTitle = styled.i`
  margin: ${props => props.theme.defaultMargin};
  font-size: 2.5vmin;
  text-align: center;
  height: 100%;
  justify-content: center;
  align-items: center;
  display: flex;
  font-weight: bold;
`
export const SalePanelDiv = styled.div`
  width: 50%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;

`
export const SalePanelContainer = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
`

export const ButtonContainer = styled.div`
  display: flex;
  justify-content: ${props => props.flexPosition};
  align-items: center;
  height: 100%;
`
