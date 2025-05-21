import styled, { keyframes } from 'styled-components'

const size = '25vmin'

const bounceX = keyframes`
  100% { transform: translateX(calc(100vw - ${size})); }
`

const bounceY = keyframes`
  100% { transform: translateY(calc(((100vh / 12) * 11.5) - ${size})); }
`

const timeX = `${(window.innerWidth / window.innerHeight) * 16}s`
const timeY = `${(window.innerHeight / window.innerWidth) * 16}s`

export const MainContainer = styled.div`
  display: flex;
  background-color: ${props => props.theme.screenBackground};
  flex-direction: column;
  width: 100%;
  height: 100%;
`

export const BackgroundDiv = styled.div`
  position: fixed;
  width: 100%;
  height: 100%;
`

export const ClickImageX = styled.div`
  height: ${size};
  width: ${size};
  animation: ${bounceX} ${timeX} linear infinite alternate;
`

export const ClickImageY = styled.div`
  background-color: ${props => props.theme.modalOverlayBackground};
  height: ${size};
  width: ${size};
  border-radius: 5vmin;
  animation: ${bounceY} ${timeY} linear infinite alternate;
`

export const ClickImage = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
`

export const ClickText = styled.div`
  color: ${props => props.theme.activeColor};
  height: 100%;
  width: 100%;
  font-size: 2.5vmin;
  text-align: center;
`
