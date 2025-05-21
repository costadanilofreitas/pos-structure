import injectSheet from 'react-jss'
import MobileTenderScreenRenderer from './renderer/MobileTenderScreenRenderer'
import DesktopTenderScreenRenderer from './renderer/DesktopTenderScreenRenderer'
import TotemTenderScreenRenderer from './renderer/TotemTenderScreenRenderer'

// eslint-disable-next-line no-unused-vars
const styles = (theme) => ({
})


const MobileRenderer = injectSheet(styles)(MobileTenderScreenRenderer)
const DesktopRenderer = injectSheet(styles)(DesktopTenderScreenRenderer)
const TotemRenderer = injectSheet(styles)(TotemTenderScreenRenderer)

export { MobileRenderer, DesktopRenderer, TotemRenderer }
