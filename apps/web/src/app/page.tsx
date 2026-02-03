'use client'

import { subscribe } from './actions'
import { useState } from 'react'

export default function Home() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  async function handleSubmit(formData: FormData) {
    setStatus('loading')
    const result = await subscribe(formData)
    
    if (result.error) {
      setStatus('error')
      setMessage(result.error)
    } else {
      setStatus('success')
      setMessage('Successfully subscribed! Check your inbox tomorrow morning.')
    }
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-50 relative overflow-hidden">
      {/* Background grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      
      {/* Decorative accent */}
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-blue-500/5 rounded-full blur-3xl" />

      <div className="relative max-w-5xl mx-auto px-6 py-16 md:py-24">
        {/* Header */}
        <header className="mb-24 md:mb-32">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
            <h1 className="text-5xl md:text-7xl font-light tracking-tight">
              every<span className="font-semibold">morning</span>
            </h1>
          </div>
          <div className="h-px w-32 bg-gradient-to-r from-cyan-400/50 to-transparent" />
        </header>

        {/* Hero Section */}
        <section className="grid md:grid-cols-[1.2fr,1fr] gap-12 md:gap-20 mb-32">
          <div>
            <h2 className="text-3xl md:text-5xl font-light leading-tight mb-8 text-zinc-100">
              Daily fresh stem paper<br />
              <span className="text-cyan-400">delivered to your inbox</span>
            </h2>
            <p className="text-lg text-zinc-400 leading-relaxed max-w-xl">
              Curated research papers from arXiv in Computer Science, Physics, Biology, and Mathematics. 
              Start your day with the latest discoveries.
            </p>
          </div>

          {/* Subscription Form */}
          <div className="relative">
            <div className="absolute -inset-4 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-2xl blur-xl" />
            <div className="relative bg-zinc-900/80 backdrop-blur-sm border border-zinc-800 rounded-xl p-8 shadow-2xl">
              <form action={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-zinc-300 mb-2">
                    Email address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    disabled={status === 'loading' || status === 'success'}
                    className="w-full px-4 py-3 bg-zinc-950 border border-zinc-700 rounded-lg text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-zinc-300 mb-3">
                    Interested in <span className="text-zinc-500">(optional, defaults to all)</span>
                  </label>
                  <div className="space-y-2.5">
                    {[
                      { id: 'cs', label: 'CS / AI / ML', value: 'cs' },
                      { id: 'physics', label: 'Physics', value: 'physics' },
                      { id: 'bio', label: 'Biology / Medical', value: 'bio' },
                      { id: 'math', label: 'Mathematics', value: 'math' },
                    ].map((field) => (
                      <label
                        key={field.id}
                        className="flex items-center gap-3 cursor-pointer group"
                      >
                        <input
                          type="checkbox"
                          name="fields"
                          value={field.value}
                          disabled={status === 'loading' || status === 'success'}
                          className="w-4 h-4 rounded border-zinc-700 bg-zinc-950 text-cyan-400 focus:ring-2 focus:ring-cyan-400 focus:ring-offset-0 focus:ring-offset-zinc-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                        <span className="text-sm text-zinc-400 group-hover:text-zinc-300 transition-colors">
                          {field.label}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={status === 'loading' || status === 'success'}
                  className="w-full px-6 py-3.5 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-zinc-950 font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 hover:scale-[1.02] active:scale-[0.98]"
                >
                  {status === 'loading' ? 'Subscribing...' : status === 'success' ? '✓ Subscribed' : 'Subscribe'}
                </button>

                {message && (
                  <div
                    className={`p-4 rounded-lg text-sm ${
                      status === 'error'
                        ? 'bg-red-500/10 border border-red-500/20 text-red-400'
                        : 'bg-cyan-500/10 border border-cyan-500/20 text-cyan-400'
                    }`}
                  >
                    {message}
                  </div>
                )}
              </form>

              <div className="mt-6 pt-6 border-t border-zinc-800">
                <a
                  href="https://t.me/everymorning_bot"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 text-sm text-zinc-400 hover:text-cyan-400 transition-colors group"
                >
                  <span>Or subscribe via Telegram</span>
                  <svg
                    className="w-4 h-4 group-hover:translate-x-1 transition-transform"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 8l4 4m0 0l-4 4m4-4H3"
                    />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </section>

         {/* How We Select Papers */}
         <section className="mb-32">
           <h2 className="text-2xl font-light text-zinc-100 mb-8">How We Select Papers</h2>
           <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-8">
             <p className="text-zinc-400 mb-6">
               Every morning, we analyze hundreds of papers from Semantic Scholar and rank them using a weighted scoring algorithm:
             </p>
             <div className="grid md:grid-cols-2 gap-6">
               {[
                 { weight: '35%', title: 'Citation Velocity', desc: 'How fast the paper is being cited relative to its age' },
                 { weight: '25%', title: 'Influential Citations', desc: 'Citations from other highly-cited papers' },
                 { weight: '20%', title: 'Recency', desc: 'Newer papers get a boost to surface fresh research' },
                 { weight: '20%', title: 'Field Diversity', desc: 'Balanced coverage across CS, Physics, Bio, and Math' },
               ].map((factor, i) => (
                 <div key={i} className="flex gap-4">
                   <div className="text-cyan-400 font-mono text-sm w-12 shrink-0">{factor.weight}</div>
                   <div>
                     <div className="text-zinc-200 font-medium">{factor.title}</div>
                     <div className="text-zinc-500 text-sm">{factor.desc}</div>
                   </div>
                 </div>
               ))}
             </div>
             <p className="text-zinc-500 text-sm mt-6 pt-6 border-t border-zinc-800">
               Each paper in your digest includes a selection reason explaining why it stood out.
             </p>
           </div>
         </section>

         {/* Features */}
         <section className="grid md:grid-cols-3 gap-8 mb-32">
           {[
             {
               title: 'Daily Digest',
               description: 'Curated papers delivered every morning at 7 AM CST',
             },
             {
               title: 'Multi-field',
               description: 'CS, Physics, Biology, and Mathematics coverage',
             },
             {
               title: 'Open Source',
               description: 'Built in public, free forever',
             },
           ].map((feature, i) => (
             <div
               key={i}
               className="group p-6 rounded-lg border border-zinc-800 hover:border-zinc-700 bg-zinc-900/30 hover:bg-zinc-900/50 transition-all duration-300"
             >
               <h3 className="text-lg font-medium text-zinc-100 mb-2">{feature.title}</h3>
               <p className="text-sm text-zinc-400 leading-relaxed">{feature.description}</p>
             </div>
           ))}
         </section>

        {/* Footer */}
        <footer className="pt-12 border-t border-zinc-800">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-zinc-500">
              © 2026 everymorning · Built for researchers, by researchers
            </p>
            <a
              href="https://github.com/xodn348/everymorning"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm text-zinc-400 hover:text-cyan-400 transition-colors group"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path
                  fillRule="evenodd"
                  d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Open source on GitHub</span>
            </a>
          </div>
        </footer>
      </div>
    </main>
  )
}
