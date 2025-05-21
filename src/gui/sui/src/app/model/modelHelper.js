import WorkingMode from './WorkingMode'
import PodFunction from './PodFunction'
import PodType from './PodType'

export function isLoginTS(workingMode) {
  return workingMode.usrCtrlType === WorkingMode.TableService
}

export function isLoginQS(workingMode) {
  return workingMode.usrCtrlType !== WorkingMode.TableService
}

export function isFrontPod(workingMode) {
  return workingMode.podType === PodType.FrontCounter
}

export function isTablePod(workingMode) {
  return workingMode.podType === PodType.Table
}

export function isTotemPod(workingMode) {
  return workingMode.podType === PodType.Totem
}

export function isFullPod(workingMode) {
  return workingMode.podType === PodType.Full
}

export function isDrivePod(workingMode) {
  return workingMode.podType === PodType.DriveThru
}

export function isOrderTakerFunction(workingMode) {
  return workingMode.posFunction === PodFunction.OrderTaker
}

export function isCashierFunction(workingMode) {
  return workingMode.posFunction === PodFunction.Cashier
}

export function isOrderPod(workingMode) {
  return isFrontPod(workingMode) || isFullPod(workingMode) || isDrivePod(workingMode)
}

export function isFullFunction(workingMode) {
  return workingMode.posFunction === '' || workingMode.posFunction === PodFunction.Full
}
