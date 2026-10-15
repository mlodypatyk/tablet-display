import { useEffect, useState } from 'react'

function pad(n: number): string {
  return n.toString().padStart(2, '0')
}

export default function Clock() {
  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  const time = `${pad(now.getHours())}:${pad(now.getMinutes())}`
  const date = new Intl.DateTimeFormat('pl-PL', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }).format(now)

  return (
    <div className="clock">
      <div className="clock__time">{time}</div>
      <div className="clock__date">{date}</div>
    </div>
  )
}
