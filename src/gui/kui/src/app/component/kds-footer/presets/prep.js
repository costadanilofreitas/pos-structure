import React from 'react'
import DisplayModeChanger from '../components/DisplayModeChanger'

export default {
  rightChildren:
    <>
      <DisplayModeChanger icon="fas fa-hand-paper" changeTo="held" className="test_Footer_WAIT" />
      <DisplayModeChanger icon="fas fa-check" changeTo="done" className="test_Footer_CHECK" />
    </>
}
