import injectSheet from 'react-jss'

import BarcodeScreenRenderer from './BarcodeScreenRenderer'

const styles = (theme) => ({
  mainBarcodeContainer: {
    borderTop: theme.defaultComponentBorder,
    boxSizing: 'border-box'
  },
  sellByBarcodeButton: {
    height: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.backgroundColor,
    color: theme.pressedBackgroundColor
  },
  barcodeProductDescriptionContainer: {
    backgroundColor: theme.backgroundColor,
    borderTop: '0.5vmin solid #DCDDDE',
    boxSizing: 'border-box'
  },
  productDescriptionBox: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    borderLeft: '0.5vmin solid #DCDDDE',
    borderBottom: '0.5vmin solid #DCDDDE',
    boxSizing: 'border-box'
  },
  productImage: {
    height: '80% !important',
    width: '80% !important',
    padding: '10%'
  },
  productDescriptionLastBox: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    borderLeft: '0.5vmin solid #DCDDDE'
  },
  productPriceBox: {
    backgroundColor: theme.backgroundColor,
    display: 'flex',
    flexDirection: 'column',
    height: `calc(100% - ${theme.defaultPadding})`,
    borderTop: theme.defaultComponentBorder,
    borderRight: '0.5vmin solid #DCDDDE'
  },
  productPriceLastBox: {
    backgroundColor: theme.backgroundColor,
    display: 'flex',
    flexDirection: 'column',
    height: `calc(100% - ${theme.defaultPadding})`,
    borderTop: theme.defaultComponentBorder
  },
  productBoxTitle: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flex: '1',
    background: theme.pressedBackgroundColor,
    color: 'white',
    margin: '0',
    lineHeight: '5vh',
    fontSize: '2.5vmin'
  },
  productBoxDescription: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flex: '2',
    margin: '0',
    fontSize: '3vmin',
    textAlign: 'center'
  }
})

export default injectSheet(styles)(BarcodeScreenRenderer)
