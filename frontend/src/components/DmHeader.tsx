import type { ReactNode } from 'react'

/** Shared header for the dark-modernist screens: wordmark left, screen-specific content right. */
export function DmHeader({ right }: { right?: ReactNode }) {
  return (
    <div className="dm-head">
      <div className="dm-word">
        Skill<span className="accent">Drill</span>
      </div>
      {right}
    </div>
  )
}
