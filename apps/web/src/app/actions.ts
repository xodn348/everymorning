'use server'

import { createClient } from '@supabase/supabase-js'

const MAX_KEYWORDS = 3

function normalizeEmail(raw: FormDataEntryValue | null) {
  return typeof raw === 'string' ? raw.trim().toLowerCase() : ''
}

function parseKeywords(raw: FormDataEntryValue | null) {
  if (!raw || typeof raw !== 'string') {
    return []
  }

  return raw
    .split(',')
    .map((keyword) => keyword.trim().toLowerCase())
    .filter(Boolean)
    .slice(0, MAX_KEYWORDS)
}

export async function subscribe(formData: FormData) {
  const email = normalizeEmail(formData.get('email'))
  const fields = formData.getAll('fields') as string[]
  const keywords = parseKeywords(formData.get('keywords'))
  
  if (!email || !email.includes('@')) {
    return { error: 'Please enter a valid email address' }
  }
  
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!
  )
  
  const existing = await supabase
    .from('subscribers')
    .select('id')
    .ilike('email', email)
    .limit(1)

  if (existing.error) {
    console.error('Duplicate subscription check error:', existing.error)
    return { error: 'Something went wrong' }
  }

  if (existing.data && existing.data.length > 0) {
    return { error: 'Already subscribed!' }
  }

  const subscriber = {
    email,
    preferred_fields: fields.length > 0 ? fields : null,
    preferred_keywords: keywords.length > 0 ? keywords : null,
  }

  let { error } = await supabase
    .from('subscribers')
    .insert(subscriber)

  // Keep existing subscriptions working until the production DB migration is applied.
  if (error && error.message?.includes('preferred_keywords')) {
    const fallback = await supabase
      .from('subscribers')
      .insert({
        email,
        preferred_fields: fields.length > 0 ? fields : null,
      })
    error = fallback.error
  }
  
  if (error) {
    if (error.code === '23505') {
      return { error: 'Already subscribed!' }
    }
    console.error('Subscription error:', error)
    return { error: 'Something went wrong' }
  }
  
  return { success: true }
}

export async function unsubscribe(email: string) {
  email = email.trim().toLowerCase()

  if (!email || !email.includes('@')) {
    return { error: 'Invalid email address' }
  }
  
  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!
  )
  
  const { error } = await supabase
    .from('subscribers')
    .update({ is_active: false })
    .eq('email', email)
  
  if (error) {
    console.error('Unsubscribe error:', error)
    return { error: 'Something went wrong' }
  }
  
  return { success: true }
}
