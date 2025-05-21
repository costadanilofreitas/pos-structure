import { I18N } from '3s-posui/core'
import styled, { css } from 'styled-components'

import React from 'react'
import PropTypes from 'prop-types'
import LinePropTypes from '../../../../../prop-types/LinePropTypes'

const ActionsContainer = styled('div')`
  width: 100%;
  height: 100%;
  display: flex;
`

const buttonStyling = {
  doing: css`
    background-color: yellow;
  `,
  done: css`
    background-color: lightgreen;
  `
}

const ActionButton = styled('button')`
  border: none;
  flex: 1;
  height: 100%;
  margin: 0;
  ${({ action }) => buttonStyling[action] ?? ''}
`

export default function LineActionsRenderer({ line, setAsDoing, setAsDone }) {
  const doing = () => setAsDoing(line)
  const done = () => setAsDone(line)


  return <ActionsContainer>
    <ActionButton
      className={'test_ActionsRenderer_NORMAL'}
      onClick={doing}
      action="doing"
    >
      <I18N id="$PREP_MODE_NORMAL"/>
    </ActionButton>
    <ActionButton
      className={'test_ActionsRenderer_DONE'}
      onClick={done}
      action="done"
    >
      <I18N id="$PREP_MODE_DONE"/>
    </ActionButton>
  </ActionsContainer>
}

LineActionsRenderer.propTypes = {
  line: LinePropTypes,
  setAsDoing: PropTypes.func,
  setAsDone: PropTypes.func
}
