import PropTypes from 'prop-types'
import DeviceType from '../../constants/Devices'


export default function RendererChooser({ deviceType, mobile, desktop, totem }) {
  if (deviceType === DeviceType.Mobile) {
    return mobile
  } else if (deviceType === DeviceType.Totem) {
    return totem
  }

  return desktop
}

RendererChooser.propTypes = {
  deviceType: PropTypes.number,
  mobile: PropTypes.object,
  desktop: PropTypes.object,
  totem: PropTypes.object
}
