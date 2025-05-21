export function getMessageKey(message) {
  let messageKey = message
  if (message.indexOf('|') >= 0) {
    messageKey = message.substring(0, message.indexOf('|'))
  }
  return messageKey.substring(1)
}
