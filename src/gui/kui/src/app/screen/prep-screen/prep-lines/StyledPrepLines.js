import styled from 'styled-components'

const Container = styled.div`
  width: 100%;
`
const PrepBody = styled.div`
  width: 100%;
  height: 100%;
  background-color: ${props => props.theme.backgroundColor};
`

export { Container, PrepBody }
