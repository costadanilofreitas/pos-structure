export default {
  buttonRoot: {
    composes: 'button-root',
    border: 'none',
    fontSize: '1.6vmin',
    outline: 'none',
    position: 'relative',
    height: '100%',
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: '0'
  },
  buttonRounded: {
    composes: 'button-rounded',
    borderRadius: '5px'
  },
  buttonFeatured: {
    composes: 'button-featured',
    border: '2px solid rgba(0, 0, 0, 0.5)',
    overflow: 'hidden'
  },
  buttonFeaturedRibbon: {
    composes: 'button-featured-ribbon fa fa-minus fa-2x',
    position: 'absolute',
    width: '10%',
    height: '10%',
    right: '-3%',
    top: '-11%',
    transform: 'rotate(45deg)',
    color: 'rgba(0, 0, 0, 0.5)'
  },
  buttonUnavailable: {
    composes: 'button-unavailable',
    backgroundColor: '#dddddd',
    color: '#878787',
    border: '1px solid #C1C1C1'
  },
  buttonUnavailableCross: {
    composes: 'button-unavailable-cross fa fa-times fa-5x',
    position: 'absolute',
    color: 'rgba(255, 255, 255, 0.5)'
  },
  buttonDisabled: {
    composes: 'button-disabled',
    backgroundColor: '#dddddd',
    color: '#878787'
  },
  buttonMenuArrow: {
    composes: 'button-menu-arrow fa',
    position: 'absolute',
    width: '100%',
    left: 0,
    top: '2%'
  },
  buttonMenuArrowUp: {
    composes: 'button-menu-arrow-up fa-chevron-up'
  },
  buttonMenuArrowDown: {
    composes: 'button-menu-arrow-down fa-chevron-down'
  },
  buttonPopupArrow: {
    composes: 'button-popup-arrow fa fa-sort-up fa-2x',
    position: 'absolute',
    top: '0',
    width: '2vh',
    right: '0',
    height: '2vh',
    transform: 'rotate(45deg)',
    msTransform: 'rotate(45deg)',
    WebkitTransform: 'rotate(45deg)'
  },
  runningIcon: {
    top: 0,
    left: 0,
    height: '100%',
    width: '100%',
    position: 'absolute',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.5)'
  }
}
