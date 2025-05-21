import styled from 'styled-components'
import { FlexGrid, FlexChild } from '3s-widgets'

const PrepHeaderRoot = styled(FlexGrid)`
  width: 99% !important;
  padding: 0 0.5% 0 0.5%;
  flex: 1;
  background-color: gray;
  color: #fff;
  font-size: 2.5vmin;
`
const PrepHeaderItem = styled(FlexChild)`
  display: flex;
  align-items: center;
  height: 90%;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
`

export { PrepHeaderRoot, PrepHeaderItem }
