import styled from 'styled-components'

import { FlexChild } from '3s-widgets'


export const ImageContainer = styled.div`
  position: fixed;
  width: 100%;
  height: 100%;
  opacity: 0.2;
  background-color: ${props => props.theme.screenBackground};
`

export const SalePanelComponent = styled(FlexChild)`
  border-top: ${props => `${props.theme.defaultPadding} solid ${props.theme.screenBackground}`};
  box-sizing: border-box;
`
