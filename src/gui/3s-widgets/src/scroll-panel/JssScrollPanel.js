import injectSheet from 'react-jss'
import ScrollPanel from './ScrollPanel'


const styles = (theme) => ({
  scrollPanelRoot: {
    composes: 'scroll-panel-root',
    position: 'absolute'
  },
  scrollPanelItemsContainer: {
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    display: 'flex',
    position: 'absolute'
  },
  scrollPanelItemsRoot: {
    width: 'auto',
  },
  scrollPanelItems: {
    composes: 'scroll-panel-items',
    backgroundColor: 'transparent !important',
    fontWeight: 700,
    fontSize: '1.5vmin',
    textRendering: 'optimizeLegibility',
    overflow: 'auto',
    width: '100%',
    height: '100%',
    '&::-webkit-scrollbar-track': {
      display: 'none'
    },
    '&::-webkit-scrollbar': {
      display: 'none'
    },
    '&::-webkit-scrollbar-thumb': {
      display: 'none'
    },
  },
  scrollPanelItemsButtonsHidden: {
    composes: 'scroll-panel-items-buttons-hidden',
    height: '100%'
  },
  scrollPanelButtonsRoot: {
    composes: 'scroll-panel-buttons-root',
    width: '100%',
    position: 'relative',
    bottom: '0'
  },
  scrollPanelButtonsCont: {
    composes: 'scroll-panel-buttons-cont',
    height: '100%',
    borderTop: '1px solid #ccc',
    margin: '-1px 0',
    display: 'flex'
  },
  scrollPanelButton: {
    composes: 'scroll-panel-button',
    fontSize: '6vmin',
    height: '100%',
    width: '100%',
    backgroundColor: 'white',
    border: 'none',
    color: '#777',
    outline: 'none',
    '&:active': {
      backgroundColor: '#777',
      color: '#eee'
    }
  },
  scrollPanelButtonUp: {
    composes: 'scroll-panel-button-up test_ScrollPanel_UP',
    float: 'left',
    fontSize: '4.0vmin !important'
  },
  scrollPanelButtonDown: {
    composes: 'scroll-panel-button-down test_ScrollPanel_DOWN',
    float: 'right',
    fontSize: '4.0vmin !important'
  },
  scrollPanelButtonUpDisabled: {
    composes: 'scroll-panel-button-up-disabled test_ScrollPanel_DISABLED-UP',
    pointerEvents: 'none',
    color: '#eee !important'
  },
  scrollPanelButtonDownDisabled: {
    composes: 'scroll-panel-button-down-disabled test_ScrollPanel_DISABLED-DOWN',
    pointerEvents: 'none',
    color: '#eee !important'
  },
  scrollPanelIconUp: {
    composes: 'scroll-panel-icon-up fa fa-caret-up test_ScrollPanel_ICON-UP',
    position: 'relative',
    backgroundColor: 'transparent'
  },
  scrollPanelIconDown: {
    composes: 'scroll-panel-icon-down fa fa-caret-down test_ScrollPanel_ICON-DOWN',
    position: 'relative',
    backgroundColor: 'transparent'
  }
})


export default injectSheet(styles)(ScrollPanel)
