import { RESYNC, EXECUTE_ACTION_REQUESTED, EXECUTE_ACTION_FINISHED } from '3s-posui/constants/actionTypes'

export default class ExecuteActionMessageBus {
  constructor(messageBus, dispatch, isActionRunning) {
    this.messageBus = messageBus
    this.dispatch = dispatch
    this.isActionRunning = isActionRunning
  }
  syncAction(actionName, ...params) {
    if (this.isActionRunning) {
      return Promise.reject({ ok: false })
    }

    this.dispatch({ type: EXECUTE_ACTION_REQUESTED })
    const promise = new Promise((resolve, reject) => {
      this.messageBus.syncAction(actionName, ...params)
        .then(data => {
          if (data.ok === false) {
            this.dispatch({ type: RESYNC })
          } else {
            resolve(data)
          }
        })
        .catch(e => {
          this.dispatch({ type: RESYNC })
          reject(e)
        })
    })

    promise.catch(() => this.dispatch({ type: RESYNC })).then(() => {
      this.dispatch({ type: EXECUTE_ACTION_FINISHED })
    })

    return promise
  }

  parallelSyncAction(actionName, ...params) {
    return this.messageBus.syncAction(actionName, ...params)
  }
}
