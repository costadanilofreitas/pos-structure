export const TableStatus = {
  Available: 1,
  Waiting2BSeated: 2,
  Seated: 3,
  InProgress: 4,
  Linked: 5,
  Totalized: 6,
  Closed: 7
}

export function getStatusLabel(status) {
  switch (status) {
    case TableStatus.Available:
      return '$AVAILABLE'
    case TableStatus.Waiting2BSeated:
      return '$WAITING_TO_BE_SEATED'
    case TableStatus.Seated:
      return '$SEATED'
    case TableStatus.InProgress:
      return '$IN_PROGRESS'
    case TableStatus.Linked:
      return '$LINKED'
    case TableStatus.Totalized:
      return '$TOTALIZED'
    case TableStatus.Closed:
      return '$CLOSED'
    default:
      return '$UNMAPPED_STATUS'
  }
}

export default Object.freeze(TableStatus)
