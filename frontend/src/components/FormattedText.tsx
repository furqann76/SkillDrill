const FENCE = /```(\w*)\n?([\s\S]*?)```/g

interface Segment {
  type: 'text' | 'code'
  content: string
}

function splitSegments(text: string): Segment[] {
  const segments: Segment[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  FENCE.lastIndex = 0
  while ((match = FENCE.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'text', content: text.slice(lastIndex, match.index) })
    }
    segments.push({ type: 'code', content: match[2].trimEnd() })
    lastIndex = FENCE.lastIndex
  }
  if (lastIndex < text.length) {
    segments.push({ type: 'text', content: text.slice(lastIndex) })
  }
  return segments
}

/** Renders plain text with ```fenced code blocks``` as <pre><code>, everything else as-is. */
export function FormattedText({ text }: { text: string }) {
  const segments = splitSegments(text)

  return (
    <>
      {segments.map((seg, i) =>
        seg.type === 'code' ? (
          <pre className="code-block" key={i}>
            <code>{seg.content}</code>
          </pre>
        ) : (
          <span key={i} className="plain-text">
            {seg.content}
          </span>
        ),
      )}
    </>
  )
}
