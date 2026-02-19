import { Clock } from 'lucide-react'

const Header = () => {
  const currentTime = new Date().toLocaleString('en-GB', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <header className="sticky top-0 z-50 bg-neutral-80 text-white shadow-md">
      <div className="max-w-[1600px] mx-auto px-4 h-12 flex items-center justify-between">
        {/* Left: Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <svg
              width="32"
              height="32"
              viewBox="0 0 32 32"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <rect width="32" height="32" rx="6" fill="#48a4d0" />
              <path
                d="M16 8L22 12V20L16 24L10 20V12L16 8Z"
                fill="white"
                fillOpacity="0.9"
              />
              <path
                d="M16 12L19 14V18L16 20L13 18V14L16 12Z"
                fill="#1a1a1a"
              />
            </svg>
            <div>
              <h1 className="text-base font-semibold leading-tight">
                Foresight AI
              </h1>
              <p className="text-xs text-neutral-400 leading-tight">
                SME Credit Risk Intelligence Platform
              </p>
            </div>
          </div>
        </div>

        {/* Right: Last Updated */}
        <div className="flex items-center gap-2 text-xs text-neutral-400">
          <Clock className="w-3.5 h-3.5" />
          <span>Last Updated: {currentTime}</span>
        </div>
      </div>
    </header>
  )
}

export default Header
