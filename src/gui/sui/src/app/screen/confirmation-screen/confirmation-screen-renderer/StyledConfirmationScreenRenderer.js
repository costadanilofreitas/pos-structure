import styled from 'styled-components'

export const Background = styled.div`
  display: flex;
  background-color: #FFF;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
  width: 100%;
  height: 100%;
`
export const Color = styled.div`
  color: ${props => props.theme.activeBackgroundColor};
  display: flex;
  align-items: center;
  justify-content: center;
`
export const ReadyColor = styled.div`
  color: ${props => props.theme.activeBackgroundColor};
  font-size: 3vmin;
`
export const ImgLogo = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
`
export const ReadyText = styled.div`
  display: flex;
  text-align: center;
  flex-direction: column;
  justify-content: center;
  font-size: 2.5vmin;
  color: #000;
  height: 100%;
`
export const BottomText = styled.div`
  display: flex;
  text-align: center;
  justify-content: center;
  font-size: 2.5vmin;
  color: #000;
  height: 100%;
  color: ${props => props.theme.activeBackgroundColor};
`
