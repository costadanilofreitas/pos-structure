import styled from 'styled-components'

export const ImageContainer = styled.div`
  width: ${props => props.containerWidth};
  height: ${props => props.containerHeight};
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.background};
  & img {
    height: ${props => props.imageHeight};
    width: ${props => props.imageWidth};
    object-fit: ${props => props.objectFit};
    max-width: 100%;
  }
`
export const RunningIcon = styled.div`
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  position: absolute;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.5)
`
export const DefaultBackground = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
`
