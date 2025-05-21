const LogisticStatus = {
  Waiting: 'Waiting',
  NeedSearch: 'NeedSearch',
  Searching: 'Searching',
  WaitingSearchingResponse: 'WaitingSearchingResponse',
  WaitingConfirmResponse: 'WaitingConfirmResponse',
  WaitingCancelResponse: 'WaitingCancelResponse',
  WaitingLogisticCancelResponse: 'WaitingLogisticCancelResponse',
  Canceled: 'Canceled',
  NotFound: 'NotFound',

  Sent: 'Sent',
  Received: 'Received',
  Confirmed: 'Confirmed',
  Finished: 'Finished'
}

export function isAwaitingLogistic(logisticStatus) {
  const awaitingLogisticStatus = [LogisticStatus.Waiting, LogisticStatus.Canceled, LogisticStatus.NotFound]
  return awaitingLogisticStatus.includes(logisticStatus)
}

export function isSearchingLogistic(logisticStatus) {
  const sentLogisticStatus = [
    LogisticStatus.Searching,
    LogisticStatus.NeedSearch,
    LogisticStatus.WaitingConfirmResponse,
    LogisticStatus.WaitingSearchingResponse
  ]
  return sentLogisticStatus.includes(logisticStatus)
}

export function isSentLogistic(logisticStatus) {
  const sentLogisticStatus = [LogisticStatus.Sent]
  return sentLogisticStatus.includes(logisticStatus)
}

export function needSearchLogistic(logisticStatus) {
  const needSearchLogisticStatus = [
    LogisticStatus.Waiting, LogisticStatus.NeedSearch, LogisticStatus.Canceled, LogisticStatus.NotFound
  ]
  return needSearchLogisticStatus.includes(logisticStatus)
}

export function confirmedLogistic(logisticStatus) {
  const confirmedLogisticStatus = [LogisticStatus.Received, LogisticStatus.Confirmed]
  return confirmedLogisticStatus.includes(logisticStatus)
}

export function isAwaitingCancellationLogistic(logisticStatus) {
  const statuses = [LogisticStatus.WaitingLogisticCancelResponse]
  return statuses.includes(logisticStatus)
}

export function hasLogisticData(logisticStatus) {
  const statuses = [LogisticStatus.Confirmed, LogisticStatus.Sent, LogisticStatus.Finished]
  return statuses.includes(logisticStatus)
}

export default Object.freeze(LogisticStatus)
