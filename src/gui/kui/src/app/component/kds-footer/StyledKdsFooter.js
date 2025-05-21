import React from 'react'
import PropTypes from 'prop-types'
import styled from 'styled-components'

import Clock from '3s-posui/widgets/Clock'

export const KdsFooterRoot = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: ${props => props.theme.tabBackgroundColor};
  color: ${props => props.theme.fontColor};
  font-size: 2.5vmin;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`

export const KdsFooterContainer = styled.div`
  display: flex;
  align-items: center;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  
  flex: ${props => {
    const { flexGrow } = props
    if (!flexGrow) {
      return 1
    }
    return flexGrow
  }};
  
  justify-content: ${props => {
    const { justifyContent } = props
    if (!justifyContent || (['start', 'center', 'end'].indexOf(justifyContent) === -1)) {
      return 'flex-start'
    }
    if (justifyContent === 'center') {
      return 'center'
    }
    return `flex-${justifyContent}`
  }};
  
  &:first-child {
    margin-left: 1em;
  }

  &:last-child {
    margin-right: 1em;
  }
`

const KdsZoomButtonBase = styled.i`
  flex: ${props => props.flexGrow ? props.flexGrow : 1};
`

export const KdsZoomButton = props => <KdsZoomButtonBase {...props} className={`fas fa-search ${props.className ?? ''}`} />

KdsZoomButton.propTypes = {
  className: PropTypes.string
}

const KdsClockContainer = styled.div`
  flex: ${props => props.flexGrow ? props.flexGrow : 2};
`
const clockStyle = {
  composes: 'kds-footer-clock',
  color: 'black',
  position: 'relative',
  display: 'table-row',
  whiteSpace: 'nowrap',
  fontSize: '2.5vmin'
}
export const KdsFullClock = (props) => (
  <KdsClockContainer {...props} flexGrow={props.flexGrow ? props.flexGrow : null}>
    <Clock showDate={false} style={clockStyle} />
  </KdsClockContainer>
)
KdsFullClock.propTypes = {
  flexGrow: PropTypes.number
}

export const KdsOrdersCounter = styled.div`
   flex: ${props => props.flexGrow ? props.flexGrow : 5};
`

export const KdsTitle = styled.div`
  width: 100%;
  text-align: center;
`

const ConsolidatedItemsButtonBase = styled.i`
  margin-left: 1em;
`
export const ConsolidatedItemsButton = props => (
  <ConsolidatedItemsButtonBase
    {...props}
    className={`fas fa-list-ol ${props.className ?? ''}`}
  />
)
ConsolidatedItemsButton.propTypes = {
  className: PropTypes.string
}

export const KdsPaginationBox = styled.div`
  margin-left: 1em;
`

const PreviousPageIconBase = styled.i`
  margin-left: 1em;
  margin-right: 0.25em;
  color: ${props => props.disabled ? props.theme.disabledIconColor : props.theme.fontColor}
`
export const PreviousPageIcon = props =>
  <PreviousPageIconBase {...props} className={`fas fa-arrow-left ${props.className ?? ''}`} />
PreviousPageIcon.propTypes = {
  className: PropTypes.string
}

const NextPageIconBase = styled.i`
  margin-left: 0.25em;
  color: ${props => props.disabled ? props.theme.disabledIconColor : props.theme.fontColor}
`
export const NextPageIcon = props =>
  <NextPageIconBase {...props} className={`fas fa-arrow-right ${props.className ?? ''}`} />
NextPageIcon.propTypes = {
  className: PropTypes.string
}

const IconBase = styled.i`
  margin-left: 1em;
`
export const KdsUndoIcon = props =>
  <IconBase {...props} className={`fas fa-undo ${props.className ?? ''}`} />
KdsUndoIcon.propTypes = {
  className: PropTypes.string
}

export const KdsRefreshIcon = props =>
  <IconBase {...props} className={`fas fa-sync ${props.className ?? ''}`} />
KdsRefreshIcon.propTypes = {
  className: PropTypes.string
}
