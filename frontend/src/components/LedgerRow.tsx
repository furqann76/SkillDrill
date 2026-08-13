import type { ReactNode } from 'react'

/**
 * The dark-modernist theme's one row component, reused for both the profile
 * list and the missed-question list: flush-left tabular index, main content,
 * optional trailing content, 2px dividers. Renders as a <button> when
 * clickable (profile picker rows), otherwise a plain <div> (missed-question
 * rows, which are informational only).
 */
export function LedgerRow({
  index,
  indexAccent = false,
  main,
  trailing,
  onClick,
}: {
  index: number
  indexAccent?: boolean
  main: ReactNode
  trailing?: ReactNode
  onClick?: () => void
}) {
  const content = (
    <>
      <span className={indexAccent ? 'dm-row-num accent' : 'dm-row-num'}>
        {String(index).padStart(2, '0')}
      </span>
      <span className="dm-row-content">{main}</span>
      {trailing && <span className="dm-row-trailing">{trailing}</span>}
    </>
  )

  if (onClick) {
    return (
      <button type="button" className="dm-row" onClick={onClick}>
        {content}
      </button>
    )
  }

  return <div className="dm-row">{content}</div>
}
