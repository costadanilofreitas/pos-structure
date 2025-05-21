import React from 'react'
import styled from 'styled-components'
import { ScrollPanel, FlexGrid } from '3s-widgets'


const ConsolidatedItemsDialogContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 4;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
`

const ConsolidatedItemsDialogBoxBase = props => <FlexGrid {...props} direction="column" />


const ConsolidatedItemsDialogBox = styled(ConsolidatedItemsDialogBoxBase)`
  position: relative;
  width: 40% !important;
  height: 70% !important;
  background-color: lightgray;
`

const ConsolidatedItemsDialogTitle = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #808080;
  font-size: 2.5vmin;
  text-align: center;
  color: white;
`

const ConsolidatedItemsDialogClose = styled.button`
  width: 100%;
  height: 100%;
  background-color: #808080;
  font-size: 2.5vmin;
  text-align: center;
  color: white;
  border: none;
`

const ConsolidatedItemsListContainer = styled(ScrollPanel)`
`

const ConsolidatedItemsList = styled.div`
  padding: 1vmin 2.5vmin;
`

export {
  ConsolidatedItemsDialogContainer,
  ConsolidatedItemsDialogBox,
  ConsolidatedItemsDialogTitle,
  ConsolidatedItemsDialogClose,
  ConsolidatedItemsList,
  ConsolidatedItemsListContainer
}
