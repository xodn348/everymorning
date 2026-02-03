'use client'

import { unsubscribe } from '../actions'
import { useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'

function UnsubscribeForm() {
  const searchParams = useSearchParams()
  const emailParam = searchParams.get('email')
  
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState(emailParam || '')

  async function handleUnsubscribe(e: React.FormEvent) {
    e.preventDefault()
    
    if (!email) {
      setStatus('error')
      setMessage('Please enter your email address')
      return
    }
    
    setStatus('loading')
    const result = await unsubscribe(email)
    
    if (result.error) {
      setStatus('error')
      setMessage(result.error)
    } else {
      setStatus('success')
      setMessage("You've been unsubscribed. We're sorry to see you go!")
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-50 relative overflow-hidden">
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-blue-500/5 rounded-full blur-3xl" />

      <div className="relative max-w-2xl mx-auto px-6 py-16 md:py-24">
        <header className="mb-16 md:mb-24">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
            <h1 className="text-4xl md:text-5xl font-light tracking-tight">
              every<span className="font-semibold">morning</span>
            </h1>
          </div>
          <div className="h-px w-32 bg-gradient-to-r from-cyan-400/50 to-transparent" />
        </header>

        <section>
          <h2 className="text-3xl md:text-4xl font-light leading-tight mb-8 text-zinc-100">
            Unsubscribe
          </h2>
          
          <div className="relative">
            <div className="absolute -inset-4 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-2xl blur-xl" />
            <div className="relative bg-zinc-900/80 backdrop-blur-sm border border-zinc-800 rounded-xl p-8 shadow-2xl">
              {status === 'success' ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-cyan-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className="text-lg text-zinc-100 mb-2">{message}</p>
                  <p className="text-sm text-zinc-400">
                    You can always <a href="/" className="text-cyan-400 hover:text-cyan-300 underline">resubscribe</a> if you change your mind.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleUnsubscribe} className="space-y-6">
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-2">
                      Email address
                    </label>
                    <input
                      type="email"
                      id="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      disabled={status === 'loading'}
                      className="w-full px-4 py-3 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      placeholder="you@example.com"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={status === 'loading'}
                    className="w-full px-6 py-3.5 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-400 hover:to-red-500 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-red-500/20 hover:shadow-red-500/30 hover:scale-[1.02] active:scale-[0.98]"
                  >
                    {status === 'loading' ? 'Unsubscribing...' : 'Unsubscribe'}
                  </button>

                  {message && status === 'error' && (
                    <div className="p-4 rounded-lg text-sm bg-red-500/10 border border-red-500/20 text-red-400">
                      {message}
                    </div>
                  )}
                </form>
              )}
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}

export default function UnsubscribePage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-zinc-950 text-zinc-50 flex items-center justify-center">
        <div className="text-zinc-400">Loading...</div>
      </main>
    }>
      <UnsubscribeForm />
    </Suspense>
  )
}
